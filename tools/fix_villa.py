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
    "10": {"name": "sendouQ second／sendouQ third dog",
            "reason": "公式「（second）…最大大人６名様まで就寝可能」＋一休「（third dog）…最大大人6名様まで就寝可能」→capacity=6（OTAの1〜9欄ではなく施設固有の明記）。pet_ok=yes は一休「ペット 可」＋公式「ペット同伴をご希望の方は『sendouQ third dog』をご利用ください。」。**ペットは third dog 棟限定で second 棟は不可**という条件付きだが、このエントリは両棟を束ねているため yes で妥当（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://sendouq.jp/price/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sendouq.jp/price/"}}},

    "12": {"name": "Villa Torami",
            "reason": "一休のプラン名2件に「最大8名様」と明記され（「ガスBBQ付、大型テラス、プライベートヴィラ、露天風呂付、最大8名様」「【1日1組限定・サウナ利用料込み】…最大8名様」）、部屋割り（BR1:2＋BR2:2＋BR3:4＝8）とも整合→capacity=8。**kitchen_type=ih を新規記録**（一休「IHコンロ、食洗器類、調理器具…」）。**sauna_type は不明のまま**: 公式「屋外サウナ完備」、一休も構造種別の明記が無い。**スキーマ外の発見**: 「屋外サウナ完備(外風呂を水風呂として利用可能)（サウナ利用はオプションとなります）」とあり、**サウナが有料オプションである旨がDBに記録されていない**。なおDBの地番「7474」に対し一休は「7474-1」と枝番の差がある（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051727/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051727/"}}},

    "38": {"name": "Asile＆OLILI",
            "reason": "**capacity を 9 から 14 に訂正し、sauna_type=barrel を削除する。** 一休を直接開いて確認したところ、住所「〒299-1861 千葉県富津市金谷517-6」はDBと一致し、両棟の情報がこう書かれていた。Asile「【Asile】プール＆サウナヴィラ 最大10様迄」「北欧から輸入したバレルサウナ。サウナストーブは電気式を採用」、OLILI「【ＯＬＩＬＩ】プール＆サウナヴィラ 最大14名様まで」「海抜25mの高台、その3階部分に海が見える室内サウナ」。**部屋タイプ欄は両棟とも「定員 1名～9名」でOTA上限そのもの**であり、既存の9はその機械的読み取り。id=113 ASH Villa で棟別（10名/6名）のときに施設全体の最大10を採ったのと同じ扱いで14とする。**sauna_type は Asile がバレル・OLILI が室内で棟により異なるため代表値を置けない。** stove=electric は Asile の「電気式を採用」に加え OLILI 公式も電気式で両棟共通のため代表値として妥当（2026-09確認）",
            "set_villa": {"capacity": "14"},
            "remove_spec": ["sauna_type"],
            "set_spec": {
                         "capacity": {"v": 14, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051536/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051536/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051536/"}}},

    "45": {"name": "HARUKA KANATA 森のヴィラ",
            "reason": "**stove を wood から electric に訂正する。居室ストーブとの混同。** 公式の「森のサウナ」の説明は「セルフロウリュウが楽しめるエストニア産のバレルサウナ」までで**熱源の記載が無い**（自分でも公式を取得して確認済み）。「薪ストーブ」の語は別セクション「体験→火のゆらめき」の「薪ストーブや焚き火が楽しめます。ご希望の場合、ご自身で薪割り体験もできます」に出てくる。サウナイキタイの構造化欄は「ドライサウナ 対流式（ストーン） 電気」と明記しており、サ活投稿も「バレルサウナはしっかり温まりますし…**お部屋では薪ストーブを焚いて**、プロジェクターで映画を見たり」とサウナと居室の薪ストーブを別物として書いている。pet_ok=yes は一休「KANATA棟、SUMIKA棟はペット不可の棟となっておりますため…ペット同伴でのご宿泊のお客様につきましてHARUKA-KANATA棟のお部屋よりご予約を」で、**2棟利用経由のみ可**という条件付きだが施設全体としては yes（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/78941"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/78941"}}},

    "49": {"name": "古民家一棟貸切旅館　成田さくら邸",
            "reason": "一休のプラン名「古民家満喫…素泊まり/定員最大9名」＋部屋タイプ「定員 2名～9名」→capacity=9（**プラン名に施設固有の数字があるのでOTA上限の遺物ではない**）。pet_ok=yes は一休「ペット 可 ペットの同伴は犬1匹まで可能です。予約時に犬種を申告ください。」。**kitchen_type=ih を新規記録**（公式「建物の古き良き雰囲気はそのままに、IHコンロ付きキッチン、檜のユニットバスなど、使いやすい設備を設置。」）（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 9, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051753/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051753/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051753/"}}},

    "209": {"name": "伊豆高原プライム",
            "reason": "出典なし3項目すべて一致した。調理器具欄「グリル付き3口ガスコンロ」→kitchen_type=gas（既存の kitchen_burners=3 とも整合）、「定員 8名」→capacity、専用の「ペット」セクションで犬・猫等2匹まで同伴可能→pet_ok=yes。**サウナ関連は未調査のまま**: ページ全体に「サウナ」の語が一度も登場しないが、resolstay は「ある物だけを列挙する」形式なので不記載を否定の根拠にできない（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/v_izukougen/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/v_izukougen/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/v_izukougen/"}}},

    "210": {"name": "熱海オーシャンハウス",
            "reason": "出典なし3項目すべて一致した。「定員 6名」→capacity、「本施設は、ペットの同伴は禁止とさせていただいております。」→pet_ok=no（明示的な否定文）、「ネット環境：Wi-Fi環境あり」→wifi。**「薪ストーブの使用について 薪ストーブの設置がありますが、ご利用いただけません。」は居室設備**で、この施設にはサウナの記載自体が無い（CLAUDE.md に記録済みの事例を再確認）（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/oceanhouse-atami/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/oceanhouse-atami/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/oceanhouse-atami/"}}},

    "215": {"name": "マイグレテラス",
            "reason": "公式の部屋一覧「1F：シアタールーム、テラス、サウナ、寝室①、寝室②、トイレ」＋専用のサウナ紹介文→sauna_exists=yes。**sauna_type=tent は根拠が見当たらない。** 公式は「サウナ」とだけ記載して構造種別を明言しておらず、**サイト内で「テント」の語が出るのは姉妹施設「マイグレ天」の広告バナー（「本格的なフィンランド式テントサウナ」）のみ**で、この施設自体の記述ではない。**類似名の別施設と混同した可能性がある。**値は残すが要再確認。**stove=electric も確定できない**（Harviaのブランド名のみ）（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/terrace"}}},

    "217": {"name": "マイグレフラット",
            "reason": "公式「縁側直結の広いウッドデッキはオーナーのこだわりが詰まった小屋サウナと露天風呂。」→sauna_exists=yes（既存の sauna_type=hut もこの一文で裏付けられる）、「オリジナルブレンドの精油アロマでお好きなだけロウリュを。」→loyly=yes。**stove=electric は確定できない**（Harviaのブランド名のみ）（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"}}},

    "234": {"name": "COCO VILLA 伊豆赤沢",
            "reason": "「COCO VILLA 伊豆赤沢では、電気式サウナを導入しています。」＋設備一覧「サウナ ◯」→sauna_exists、スペック表「ととのいスペース ◯」「外気浴 ◯」「ととのい用チェア ◯」→outdoor_rest。**sauna_type=hut は確定できない**: 「離れ」「サ室」とのみ記載され hut/indoor/tent/barrel いずれの語も無い。**なお「サウナ用ハット」は頭にかぶるウールの帽子であって構造ではない**ので誤読しないこと（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/izuakazawa/"}}},

    "238": {"name": "月と太陽",
            "reason": "**capacity を 5 から 10 に訂正する。** 一休と公式に4棟の定員が明記されている: DREAM VILLA 5名 / HANABI 6名 / BASE ATAMI 10名 / EN ATAMI 10名。**既存の5は最小の DREAM VILLA の数字**で、施設全体の代表値ではない。各棟独立予約のため「全棟利用時の合計」という数字は存在しないが、**id=113 ASH Villa（10名/6名の2棟）で施設全体の最大10を採ったのと同じ扱い**にする。sauna_exists=yes は「全ての施設で、温泉・サウナ・バーベキューをお楽しみいただけます。」（4棟共通）、pet_ok=yes は「月と太陽は犬と泊まれる貸別荘。…ワンちゃん（小型犬に限ります）」＋一休「ペット 可」。**なお一休の住所はチェックイン受付「熱海自然郷フォレストカフェ」のもので、4棟はそれぞれ別住所**（一休自体がこの代表住所を使っているのでDBの扱いは妥当）（2026-09確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051474/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051474/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051474/"}}},

    "244": {"name": "HAKU-AKAZAWA- 【波空】",
            "reason": "公式「1階のサウナスペースにはサウナ好きの方にもご満足いただける、本格的な設備が揃っています。」→sauna_exists、「水風呂は温度14度前後、バイブラ付き。」→coldbath=bath。**capacity=8 は確定できない**: 公式・一休とも「定員」「最大N名」の明記が無く、一休は「客室数 1室」のみ。一休の口コミに「8人での利用でしたが…インフィニティチェアも4台あり」という宿泊者の記述はあるが、口コミは根拠にしない（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://haku-resort.com"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://haku-resort.com"}}},

    "270": {"name": "COCO VILLA 長瀞",
            "reason": "出典なし3項目すべて一致した。「本施設では、電気式サウナを導入しています。」＋設備一覧「サウナ ◯」→sauna_exists、「水風呂・シャワー」＋「水風呂収容人数 1名」＋ハウスルール「水風呂をご用意しています。…水を抜くように」→coldbath=bath、スペック表「ととのいスペース ◯」「外気浴 ◯」＋「Coleman インフィニティチェア（2台）／ととのい用ベンチ（1台）」→outdoor_rest。**既存の rest_chair=infinity も「Colemanインフィニティチェア」と完全に一致**していた（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/nagatoro/"}}},
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
