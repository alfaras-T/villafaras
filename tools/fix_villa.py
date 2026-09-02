#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys

# set_villa で触る VILLAS のスカラー項目。villas/*.html では fact 行としても描画される。
VILLA_FACTS = {
    "capacity": ("定員", "%s名"),
    "checkin":  ("チェックイン", "%s"),
    "checkout": ("チェックアウト", "%s"),
}


def json_obj_end(s, i):
    """JSON オブジェクトの開き波括弧 i から、対応する閉じ括弧の次の位置を返す。"""
    if i < 0 or i >= len(s) or s[i] != "{":
        return -1
    depth = 0
    while i < len(s):
        c = s[i]
        if c == '"':
            i += 1
            while i < len(s) and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1

FIXES = {
    "18": {"name": "On the wave 館山",
            "reason": "一休の宿のご紹介「カリフォルニア風サーファーズハウス…**1階にLDKとお風呂とサウナ**。2階には寝室（トイレ付き）が2つ」→sauna_type=indoor（母屋1階の室内設備）。「サウナ室の窓からは海と庭を見渡すことができる」とも整合。**stove は入れない**: 一休に「HEARVIA製のサウナストーブを設置」とあるがHARVIA社は薪式・電気式の両方を製造している（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052150/"}}},

    "29": {"name": "PRIVE",
            "reason": "サウナイキタイの構造化欄「外気浴 デッキチェア：2席」→outdoor_rest=yes。**この施設は公式サイトにサウナの記載が一切ない**（CLAUDE.md の既知5件と同じパターン）。**loyly は入れない**: サウナイキタイの「ロウリュ（アウフグース） スタイル：その他」は yes/auto/no のいずれにも対応しない（2026-09確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/87598"}}},

    "32": {"name": "moe-akala,moe-aina",
            "reason": "**capacity=9（2026-07・出典なし）は誤り。13 が正しい。** 一休を直接開いて確認したところ、部屋情報の定型欄は「akala or aina 定員 1名～9名」だが、**プラン本文は「【愛犬同伴無し／最大13名】」「【愛犬同伴OK／最大13名】」と一貫して13名**と書いている。同ページの kai or mana は「定員 1名～5名」でプラン名も「最大5名様」と整合しており、9だけが浮いている。**CLAUDE.md に記録済みの Noёl HAKONE GENSEN（「一休のサイト仕様上9名様しか予約ができません」）と同型のパターン。** akala と aina は同一敷地内の同一仕様の双子棟で一休の部屋名も「akala or aina」と一体表記のため、単棟の数字を代表値にしてよい。kitchen_type はプラン詳細ページの「アイランドキッチン（IH）、カウンターチェア4脚…」、wifi は公式FAQ「接続可能です。・wi-fiが利用可能です。」＋一休「無料Wi－Fi」。**stove は入れない**: 「バレルロウリュウサウナ」は形式の呼称で熱源ではない（2026-09確認）",
            "set_villa": {"capacity": "13"},
            "set_spec": {
                         "capacity": {"v": 13, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051962/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051962/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051962/"}}},

    "50": {"name": "THE CLUB 919 DOG FRIENDLY",
            "reason": "公式の設備一覧の**＜室内＞欄**に「…床暖房、トレーニングマシーン3台、サウナ、ジャグジー」と記載されており、＜屋外＞欄（温水プール、シャワー等）と明確に区分されている→sauna_type=indoor。**coldbath は入れない**: 屋外プールは「冬でも33°Cまで上がる温水」と明記されており水風呂に該当しない。**stove も入れない**: 暖房は床暖房・エアコンで、サウナ単体の熱源記述が無い（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://theclub919.com/facilities/"}}},

    "90": {"name": "totonoco 湖畔の隠れ家",
            "reason": "公式の間取り「【2F】キッチン+リビング+半露天風呂+サウナ」＋一休「客室半露天風呂・サウナ」「2階客室風呂・サウナ・リビングからの眺望」→sauna_type=indoor（客室内設備として位置づけられている）（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/totonoco/"}}},

    "233": {"name": "Hiire IZU OMURO",
            "reason": "公式の「しつらえ」バスルーム欄「専用バスルーム／客室サウナ／シャワー／バスタブ…」→sauna_type=indoor。同ページは「Hiireは三つの棟に分かれています」として OLIVE / OMURO / FUTO を名指ししているため流用ではない。既存の capacity=6 も一休「Hiire IZU OMURO（サウナ・温泉・囲炉裏付き）一棟貸し 定員 1名～6名」で裏付け（9ではないので採用可）。**stove は入れない**: 「エストニア製のサウナをご用意」は原産国であって熱源ではない（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://hi-ire.com/stay"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://hi-ire.com/stay"}}},

    "237": {"name": "Tiny Base The Irita-hama",
            "reason": "公式トップ「各施設エリア内に専用のサウナがあります…温度は、90～110度 薪の良い香りに、セルフロウリュ サウナ室を出てすぐ入れる水風呂と、ととのいスペース…※The River TRAILER/The Valley/**The Irita-hama は電気式サウナストーブです**」→loyly=yes / coldbath=bath / outdoor_rest=yes。**既存の stove=electric はこの脚注と /stay/ ページの「サウナ（電気式）」の2箇所で裏付けが取れた。**なお共通説明の「薪の良い香り」は電気式の当施設には当てはまらないため、その部分は根拠にしていない（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp"}}},

    "242": {"name": "the villa Oka 伊豆高原温泉",
            "reason": "公式noteガイド「1階屋外スペースにはサウナ小屋を設置しました。内部には…**MISA製の電気ストーブを採用、火を使うことなく安全に**…」→stove=electric（**サウナ内部の設備として熱源が明記されている**）。pet_ok=no は一休の設備欄「× ペット可」＋基本情報「ペット 不可」で、公式にもペットの記載が無く矛盾しない。既存の sauna_exists=yes と capacity=6 も裏付けが取れた（公式note「ご宿泊人数は6名様までとなっております。」／公式サイト「定員 : 6」／一休「定員 1名～6名」の3ソース一致）。**sauna_type は入れない**: 同じ段落に「サウナ小屋を設置しました」と「テントサウナをお楽しみいただけます」が混在しており**公式情報源の内部で矛盾している**。**coldbath も入れない**: 設備一覧の「サウナ／屋外シャワー／ととのい椅子」の並びから shower が推測できるが、水風呂自体の記載がどこにも無く並び順からの推測にすぎない（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"}}},

    "251": {"name": "LAMERVON",
            "reason": "**公式サイトにサウナの記載が一切ない施設（6件目）。** ankr-resort.team の施設紹介ページ全文を確認したが、リビング／アウトドアリビング／ラウンジ／和室／メインベッドルームの説明にサウナへの言及が無い。一方 ACO には「本格サウナ完備！サウナ後は滝行シャワーを浴びることが出来ます」「外デッキではサウナ・BBQが楽しめます」と写真付きで明記されており、既存の sauna_exists=yes は妥当。capacity=10 も ACO「定員: 10人迄」で、公式の各部屋人数の合算（メインベッド2＋和室2＋シングル1＋コミックラウンジ1＋ラウンジソファベッド2＋リビングソファベッド2）とも一致する。**stove は入れない**: ACOページ下部に「薪ストーブ」の語が出るが、これは本施設の説明ではなくサイト内の他施設横断テーマ別リンク一覧（「ペット可屋根付BBQ温泉ログハウス古民家…薪ストーブ…」の羅列）に紛れ込んだもの（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.aco.co.jp/id/65979.html"},
                         "capacity": {"v": 10, "src": "desk", "at": "2026-09",
                                        "url": "https://www.aco.co.jp/id/65979.html"}}},

    "256": {"name": "パーパスリゾート EG Sky Terrace 熱川",
            "reason": "公式ハウスマニュアルPDFのサウナ項「**ご使用になる前に電源ダイヤルをON方向へまわしてください**。ヒーターストーンでロウリュウをお楽しみいただけます。」→stove=electric / loyly=yes（サウナイキタイの構造化タグ「ドライサウナ 対流式（ストーン） 電気」とも一致）。「フレグランスオイルをご利用の際は必ず！ロウリュウ専用のフレグランスをご使用ください。」も補強。outdoor_rest はサウナイキタイ「外気浴 寝転べるイス（フルフラット可）：4席」＋公式浴室の項「窓を開けると外気浴をお楽しみいただけます」。既存値も裏付けが取れた: sauna_type=barrel はサウナイキタイのプラン名「1棟貸切 屋外バレルサウナとプールプラン」、capacity=12 は公式「コンドミニアムタイプ…定員12名」、pet_ok=yes は公式FAQ「はい、ペット同伴でご宿泊いただけます。」。**kitchen_type は入れない**: 「30分以上連続でガスを使用すると、自動的に停止する場合があります。」が設備一覧の「その他」欄にありBBQの記載とも混在しているため、キッチンのコンロを指すか断定できない（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.purposeresort.com/img/house_manual_atagawa.pdf"}}},

    "273": {"name": "HOLE37",
            "reason": "サウナイキタイの構造化タグ「アウトドアサウナ＞サウナ小屋（屋外・水着着用）○」→sauna_type=hut、「ドライサウナ 対流式（ストーン） 電気」→stove=electric。**TYLO というメーカー名は根拠にしていない**（薪式・電気式の両方を製造するため）。投稿の「自分で温度は95℃に設定」という操作性の記述を補強に使った。outdoor_rest は公式 /sauna「夜には満天の星空のもと、デッキチェアを広げて堪能する極上の外気浴が待っています。」＋サウナイキタイ「外気浴 寝転べるイス：2〜3席」。既存値も裏付け: coldbath=bath は公式「熱った身体を待ち受けるのは、一人専用ドラム缶の水風呂。」、capacity=6 は一休「定員 1名~6名」（9ではない）。**なお投稿に「ドラム缶とバスタブタイプの2種類」という記述があり棟で設備が違う可能性がある**（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/79299"}}},
}

DRY = "--dry-run" in sys.argv


def write(path, s, orig):
    if s == orig:
        print("    変更なし: %s" % path)
        return 0
    if DRY:
        print("    [dry-run] %s を更新予定" % path)
    else:
        io.open(path, "w", encoding="utf-8").write(s)
        print("    更新: %s" % path)
    return 1


for vid, fx in FIXES.items():
    print("\n=== id=%s %s ===" % (vid, fx["name"]))
    print("  理由: %s" % fx["reason"])

    p = "index.html"
    s = orig = io.open(p, encoding="utf-8").read()
    villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL).group(1))
    tgt = [v for v in villas if str(v["id"]) == vid]
    if not tgt:
        print("  !! VILLAS に見つかりません"); continue
    cur_tags = tgt[0].get("tags") or []

    for t in fx.get("remove_tags", []):
        if t not in cur_tags:
            print("    tag '%s' は既にありません" % t); continue
        new_tags = [x for x in cur_tags if x != t]
        # 同じタグ構成の別施設を誤爆しないよう、対象施設のオブジェクト内に限定して置換する。
        # VILLAS の各要素は tags -> id の順に並ぶので、"id": N の直前の "tags": [...] が対象。
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        cands = list(re.finditer(r'"tags":\s*(\[[^\]]*\])', s[:mid.start()]))
        if not cands:
            print("    !! tags が見つかりません"); continue
        last = cands[-1]
        if json.loads(last.group(1)) != cur_tags:
            print("    !! tags が一致しません（%s）" % last.group(1)); continue
        rep = json.dumps(new_tags, ensure_ascii=False)
        if '", "' not in last.group(1):
            rep = rep.replace('", "', '","')
        s = s[:last.start(1)] + rep + s[last.end(1):]
        print("    tags: %s -> %s" % (cur_tags, new_tags))
        cur_tags = new_tags

    for t in fx.get("add_tags", []):
        if t in cur_tags:
            print("    tag '%s' は既にあります" % t); continue
        new_tags = cur_tags + [t]
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        cands = list(re.finditer(r'"tags":\s*(\[[^\]]*\])', s[:mid.start()]))
        if not cands:
            print("    !! tags が見つかりません"); continue
        last = cands[-1]
        if json.loads(last.group(1)) != cur_tags:
            print("    !! tags が一致しません（%s）" % last.group(1)); continue
        rep = json.dumps(new_tags, ensure_ascii=False)
        if '", "' not in last.group(1):
            rep = rep.replace('", "', '","')
        s = s[:last.start(1)] + rep + s[last.end(1):]
        print("    tags: %s -> %s" % (cur_tags, new_tags))
        cur_tags = new_tags

    # VILLAS のスカラー項目。同じ値を持つ別施設を誤爆しないよう、
    # "id": N を含む施設オブジェクトの範囲内に限定して置換する。
    old_vals = {}
    for k, val in (fx.get("set_villa") or {}).items():
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        st = s.rfind('{"name"', 0, mid.start())
        en = json_obj_end(s, st)
        if st < 0 or en < 0:
            print("    !! id=%s の施設オブジェクト範囲を特定できません" % vid); continue
        seg = s[st:en]
        mk = re.search(r'("%s":\s*)"([^"]*)"' % re.escape(k), seg)
        if not mk:
            print("    !! %s が見つかりません" % k); continue
        if mk.group(2) == str(val):
            print("    %s は既に %s" % (k, val)); continue
        print("    %s: %s -> %s" % (k, mk.group(2), val))
        old_vals[k] = mk.group(2)
        s = s[:st] + seg[:mk.start()] + '%s"%s"' % (mk.group(1), val) \
            + seg[mk.end():] + s[en:]

    if fx.get("old_desc"):
        n = s.count(fx["old_desc"])
        if n:
            s = s.replace(fx["old_desc"], fx["new_desc"])
            print("    desc: %d 箇所を差し替え" % n)
        else:
            print("    !! desc が一致しません（index.html）")
    write(p, s, orig)

    for p in glob.glob("villas/%s-*.html" % vid):
        s = orig = io.open(p, encoding="utf-8").read()
        if fx.get("old_desc"):
            s = s.replace(fx["old_desc"], fx["new_desc"])
            for t in set(re.findall(r'content="([^"]{40,}?)…"', s)):
                if t and fx["old_desc"].startswith(t):
                    s = s.replace(t + "…", fx["new_desc"][:len(t)] + "…")
                    print("    meta 短縮版を差し替え")
        for k, val in (fx.get("set_villa") or {}).items():
            # fact 行ではないが本文中にそのまま出る項目（official など）は
            # 旧い値を新しい値に置き換える。個別ページは1施設分なので誤爆しない。
            if k not in VILLA_FACTS:
                old = old_vals.get(k)
                if old and old in s:
                    n = s.count(old)
                    s = s.replace(old, val)
                    print("    %s を %d 箇所差し替え -> %s" % (k, n, val))
                continue
            label, fmt = VILLA_FACTS[k]
            new = fmt % val
            s2 = re.sub(r'(<span class="fact-label">%s</span>'
                        r'<span class="fact-val">)[^<]*(</span>)' % re.escape(label),
                        lambda m: m.group(1) + new + m.group(2), s, count=1)
            if s2 != s:
                print("    fact「%s」を %s に更新" % (label, new))
                s = s2

        # add_tags は pill も足す。既存 pill と同じ書式に合わせるため、
        # 他ページから同じラベルの pill をひな型として拾う。
        for t in fx.get("add_tags", []):
            label = {"sauna": "サウナ", "pet": "ペットOK", "bbq": "BBQ",
                     "onsen": "温泉", "pool": "プール"}.get(t)
            if not label or ('>%s</span>' % label) in s:
                continue
            tmpl = None
            for q in glob.glob("villas/*.html"):
                m = re.search(r'<span class="pill" style="[^"]*">%s</span>' % label,
                              io.open(q, encoding="utf-8").read())
                if m:
                    tmpl = m.group(0); break
            if not tmpl:
                print("    !! pill「%s」のひな型が見つかりません" % label); continue
            m2 = re.search(r'(<span class="pill"[^>]*>[^<]*</span>)', s)
            if m2:
                s = s[:m2.end()] + tmpl + s[m2.end():]
                print("    pill「%s」を追加" % label)

        for t in fx.get("remove_tags", []):
            label = {"sauna": "サウナ", "pet": "ペットOK", "bbq": "BBQ",
                     "onsen": "温泉", "pool": "プール"}.get(t)
            if label:
                s2 = re.sub(r'<span class="pill"[^>]*>' + re.escape(label) + r'</span>',
                            "", s, count=1)
                if s2 != s:
                    print("    pill「%s」を削除" % label)
                    s = s2
        write(p, s, orig)

    p = "spec-data.js"
    s = orig = io.open(p, encoding="utf-8").read()
    m = re.search(r'(^  "%s": \{.*?\n  \},?)' % vid, s, re.M | re.S)
    if m:
        blk = m.group(1)
        nb = blk
        for k in fx.get("remove_spec", []):
            nb = re.sub(r"\n    %s:\s*\{[^}]*\},?" % re.escape(k), "", nb)
        for k, val in (fx.get("set_spec") or {}).items():
            body = "{ " + ", ".join(
                "%s: %s" % (kk, json.dumps(vv, ensure_ascii=False).replace('"', "'")
                            if isinstance(vv, str) else vv)
                for kk, vv in val.items()) + " }"
            mk = re.search(r"\n(\s*)%s:(\s*)\{[^}]*\}" % re.escape(k), nb)
            if mk:
                old = mk.group(0)
                new = "\n%s%s:%s%s" % (mk.group(1), k, mk.group(2), body)
                if old != new:
                    nb = nb.replace(old, new, 1)
                    print("    spec: %s を更新 -> %s" % (k, body))
                else:
                    print("    spec: %s は既に同値" % k)
            else:
                nb = nb.replace("\n  },", "\n    %s: %s,\n  }," % (k, body), 1) \
                     if "\n  }," in nb else nb
                print("    spec: %s を追加 -> %s" % (k, body))
        nb = re.sub(r",(\s*\n  \},)", r"\1", nb)
        # 項目を追加したとき、それまで最後だった項目にはカンマが無い。
        # 補わないと "}" の直後に次の項目が続いて JS の構文エラーになる。
        # 波括弧の対応は取れてしまうので validate.py の括弧検査では気づけない。
        nb = re.sub(r"\}\n(\s+)(\w+):", r"},\n\1\2:", nb)
        if nb != blk:
            s = s.replace(blk, nb, 1)
            if fx.get("remove_spec"):
                print("    spec: %s を削除" % ", ".join(fx["remove_spec"]))
        write(p, s, orig)
    else:
        print("    spec-data.js に該当なし")

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
