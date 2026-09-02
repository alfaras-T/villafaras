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
    "39": {"name": "VILLA UMICHIKA 九十九里一宮",
            "reason": "公式「申し訳ございませんが、ペットの同伴はお断りしております。」＋一休の設備欄「× ペット可」・基本情報「不可」→pet_ok=no、公式「Wi-Fi完備」＋一休「wi-fiが利用可能です」。既存の capacity=8 も公式「PRIVATE VILLA 6886：定員 最大8名」で裏付け（DBの住所 東浪見6886-2 は PRIVATE VILLA 6886 と一致。同施設にはもう1棟 POOL & SAUNA VILLA 6885 がある）。**stove は入れない**: 「国産ヒノキのバレルサウナ」までで熱源の言及が無い（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://umichika.jp/villa/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://umichika.jp/villa/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://umichika.jp/villa/"}}},

    "42": {"name": "雫花",
            "reason": "公式FAQ「申し訳ございませんが、ペット同伴でのご宿泊はご遠慮いただいております。」＋一休「ペット 不可」→pet_ok=no、FAQ「無料のWi-Fiを全館で備えております。」→wifi=yes（「全館」なので両棟共通）。既存の capacity=2 も一休で Private Villa「定員 2名」・Luxury Villa「定員 1名～2名」の両棟とも2で一致し、FAQ「恐れ入りますが、部屋数が少ないため大人2名様からでお願いしております」とも整合。**同一住所に Private Villa（35㎡）と Luxury Villa（130㎡）の2棟があり、既存の stove / loyly / coldbath は Private Villa のページを出典にしている**（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://sizca.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sizca.jp/faq/"},
                         "capacity": {"v": 2, "src": "desk", "at": "2026-09",
                                        "url": "https://sizca.jp/faq/"}}},

    "100": {"name": "MT.FUJI SKY CABIN",
            "reason": "公式のお知らせ「キャビン内には４つのベット」で既存の capacity=4 を裏付けた。一休は「定員 1名～6名」だが**「シングルベッドが４台になりますので、５名様目のベッドのごよういはございません」という注記付き**で、6はベッド無しでも詰め込める上限。**stove は入れない**: 公式に「暖房（石油ストーブをご用意しております）」とあるが、これは「キッチン」「その他」の見出しに属する**居室の暖房設備**であり、しかも石油はスキーマの wood/electric/gas のどれでもない（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://mtfuji-camp-resort.jp/info/mt-fuji-sky-cabin/"}}},

    "103": {"name": "Private villa FujiNagi",
            "reason": "公式「テラス：バレルサウナ/ロウリュウセット/水風呂/インフィニティチェア」→coldbath=bath。**季節制限（スキーマ外）**: 同ページに「※冬季は凍結防止のため屋外の水風呂、シャワー、水栓の使用を休止させて頂きます。サウナから内風呂にすぐアクセスできますので、内風呂を水風呂代わりにご利用ください。」とある。**loyly は入れない**: 「ロウリュウセット」という器具の存在からセルフが推測できるが明言が無い。**stove も入れない**: サウナの説明に熱源が無く、リビングの「ガスヒーター」は別見出しの居室設備（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.fujinagi.com/overview-facility.html"}}},

    "111": {"name": "HOTEL SEION FUJI",
            "reason": "**メーカー名ではなく型番だったので熱源が確定できた。** 公式「ストーブは、HARVIAのCILINDROを採用しています」。Harvia社は薪式・電気式の両方を製造するためブランド名だけでは決められないが、**CILINDRO は電気ヒーター専用のシリーズ**（型番 PC60E / PC132E、200V・6.9kW など。薪式のラインナップが存在しない）。独立した検索で確認した。既存の stove=electric は正しい。**sauna_type は入れない**: 「大きく開かれたガラス越しに四季を楽しめるサウナ」までで形式不明。**loyly も入れない**: Cilindro が一般にロウリュ対応であることは製品仕様の一般論で、この施設がセルフ運用を許可しているかの明言ではない（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://fuji.hotel-seion.com"}}},

    "116": {"name": "Kito NASU",
            "reason": "公式予約サイト「当施設はペット利用不可です。万が一ご利用になられた場合、室内クリーニング費と営業補償費をお客様自身にご負担いただきます。」＋一休の基本情報「ペット：不可」→pet_ok=no。**水源のスキーマ不足を再確認**: 一休に「屋根から流れ落ちた雨水は窪んだ穴に溜まり、「水たまり」のような水風呂になります。」とあり、water_src の選択肢（tap/well/spring/river）のどれにも該当しない（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://kito-nasu.booking.chillnn.com/ja/"}}},

    "122": {"name": "Earthboat Nasu",
            "reason": "公式「IHコンロ」→kitchen_type=ih、客室設備「Wi-Fi」→wifi=yes。sauna_type=hut はサウナイキタイのアウトドアサウナ欄「サウナ小屋（屋外・水着着用）：○」（他のテント/サウナカー等は全て「-」）で、**このページは登録者が「Earthboat｜地球を肌で感じる宿」と施設自身**なので投稿ベースより確度が高い。既存値も裏付けが取れた: stove=wood は公式「フィンランド式サウナ（薪ストーブ）」＋一休「薪ストーブ式」、loyly はサウナイキタイ「セルフロウリュ：プライベートのため、自分の好みに合わせて利用可能」、coldbath は公式「水風呂（一部客室は温水利用可）」、outdoor_rest は公式の客室設備「インフィニティチェア」、capacity=3 は公式「定員 3名」＋サウナイキタイ「最大3名」、pet_ok=yes は公式「ペットの受け入れ 可（種類・大きさ・頭数の制限なし）」（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "capacity": {"v": 3, "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"}}},

    "161": {"name": "Oceanfront Villa Hale Kahakai",
            "reason": "公式「そして晴れた日には、目の前に広がる金田湾と潮風を感じながら外気浴。」「2階のウッドデッキに座り、波の音を聞きながら」→outdoor_rest=yes。既存の sauna_exists=yes も極めて明確な記述で裏付けられた: 「屋内100℃のMETOS製本格高温ドライサウナです。**屋外に設置された簡易的なバレルサウナではなく、本格的なサウナ設備をヴィラの建物内に設置しています。**」（既存の sauna_type=indoor / stove=electric も強く支持する）（2026-09確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/"}}},

    "166": {"name": "in the meantime",
            "reason": "公式FAQ「ペットと一緒に宿泊できますか？」→「申し訳ございません。ペット同伴でのご宿泊はできません。」＋一休の基本情報「ペット：不可」→pet_ok=no。既存値も裏付けが取れた: sauna_exists はFAQ「はい。一棟貸しのため、ご滞在中は宿泊者のみでフィンランド式のプライベートサウナをご利用いただけます。」、capacity=8 はFAQ「最大8名様までご宿泊いただけます。寝室は3室あり、寝室1にシングルベッド2台、寝室2にシングルベッド2台、和室に布団3組、リビングにソファベッド1台」（2+2+3+1=8で計算も一致）。**stove は入れない**: 公式全体に「ストーブ」「HARVIA」等の語が一切無い。**WebSearchの要約が「wood stove がアメニティに含まれる」と述べ aco.co.jp を出典としたが、同ページを直接取得すると「薪ストーブ」の語は一度も出現しなかった**（施設をまたいだ混同の実例）（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://in-the-meantime.jp/faq/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://in-the-meantime.jp/faq/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://in-the-meantime.jp/faq/"}}},

    "212": {"name": "熱海リゾート",
            "reason": "既存値に出典を付ける。sauna_exists は「館内には熱海温泉を引いた浴室に加え、新たにサウナを導入」、sauna_type=indoor は「【サウナ】・サウナは**室内**にある2名用です。」と明確、kitchen_type=ih は【家電】欄の「IHコンロ(2口)」（既存の kitchen_burners=2 とも整合）。**coldbath は bath のまま変更しない**: 「浴槽は二つあり、温泉と水風呂を行き来する本格的な『ととのう体験』も可能です。」を id=144 と同型として tub への訂正が提案されたが、**id=144 の決め手は「もしくはお湯を入れることができます」という切り替え可能性**であり、ここでは2つ目の浴槽が水風呂専用と読める。tub は兼用のための選択肢なので当てはまらない。**stove も入れない**: 【家電】欄の「ストーブ」はテレビ・IHコンロ・冷凍冷蔵庫・冷暖房エアコンと並ぶ**居室の家電**で、サウナの説明箇所とは別セクション（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamiresort/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamiresort/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamiresort/"}}},

    "217": {"name": "マイグレフラット",
            "reason": "公式「フィンランド式**サウナ小屋**とホームシアターが自慢の一棟貸し別荘」「縁側直結の広いウッドデッキはオーナーのこだわりが詰まった**小屋サウナ**と露天風呂」→sauna_type=hut。既存値も裏付け: coldbath=bath は「お風呂 露天風呂(伊東天然温泉)・水風呂・オーバーヘッドシャワー・内風呂」、capacity=5 は「定員 5名」（範囲表記ではなく単一の数字）、wifi=yes は「Wi-Fi 完備」。**stove=electric は今回も裏付けが取れなかった**: 「超高熱度の本格的フィンランド製HARVIAサウナストーブを直輸入」とブランド名のみで、id=111 の CILINDRO のような型番も「方式：電気式」のような専用欄も無い。**マイグレ15施設の一律適用の疑いを追加で1件裏づける結果**。**同ページのInstagram埋め込みに「セルフロウリュ」等の文言があったが、投稿の住所は「静岡県伊東市吉田890-33」で別施設 MAIGRE 600 のものだった**ため採用していない（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"},
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/flat"}}},
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
