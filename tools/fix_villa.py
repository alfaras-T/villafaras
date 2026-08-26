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
    "146": {"name": "TIMeSCAPE -hakone-",
            "reason": "「檜のサウナから、山の緑と空に心癒される」「現時点ではペットの同伴は承っておりません」「当施設の敷地内でFree Wi-Fiをお使いいただけます」、FAQ「自然に囲まれた水風呂」「木々のゆらめきを浴びながら外気浴をご堪能ください」。サウナは材質（檜）の記述のみで構造が非公表のため sauna_type は入れない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://timescape-hakone.jp/faq/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://timescape-hakone.jp/faq/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://timescape-hakone.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://timescape-hakone.jp/faq/"}}},

    "150": {"name": "3rd HOUSE INAMURAGASAKI",
            "reason": "「屋上にございますサウナ」「ペット立ち入り可能エリアは、3階ペットルームのほか…屋外部分」「Wi-fi環境：下り250Mdps／上り220Mdps」。定員は西棟8名／東棟6名で棟により異なるうえ西棟が資料により8名／9名で食い違うため変更しない。coldbath は「ジャグジー」の言及のみで「水風呂」の語が出ないため入れない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://3rd-house.jp/mustread/forguest/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://3rd-house.jp/mustread/forguest/"}}},

    "153": {"name": "UMITO VILLA KAMAKURA ZAIMOKUZA",
            "reason": "「プライベートサウナを備え、湯船からも海を眺められる特別な空間」「宿泊定員：4名」「愛犬同伴対応」。水風呂の記載あり。**sauna_exists は yes のまま変更しない**（1棟のヴィラで「一部客室のみ」を示す記述はない）。wifi の出典 /qa は材木座固有ではなくUMITOブランド共通FAQのため入れない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel.umito.jp/kamakura-zaimokuza/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel.umito.jp/kamakura-zaimokuza/"}}},

    "157": {"name": "TANZAWA seven lanes by DAICHI",
            "reason": "施設独自サイトを新たに特定。DAICHI公式と一休の2ソースで「テントサウナ」が一致。「Capacity 1~8 people」も chillnn と一休の2ソースで一致。「Pet Not allowed」。sauna_hours は当初「サウナストーブの連続使用は40分まで」を根拠にしかけたが**これは葉山THE・TERRACE HOUSE の情報**と判明したため入れない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://www.7lanes.jp/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.7lanes.jp/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.7lanes.jp/"}}},

    "159": {"name": "葉山THE・TERRACE　HOUSE",
            "reason": "公式はJS描画で取得不可のため代理店サイトを出典とする。「屋上の使用時間（バーベキュー・サウナ）は21時までとなっております」「サウナストーブの連続使用は40分までにお願いいたします」→sauna_hours=limited、「定員10名」「ペット同伴不可」「Wi-Fiも無料でご利用いただけます」。sauna_type=barrel は二次情報2件の一致による。WebSearch要約が「ドライサウナとバレルサウナ」と混在的に述べたが公式系の代理店サイトは終始バレルサウナのみを描写するため後者を採った（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://tripto.jp/facilities/425"},
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                        "url": "https://tripto.jp/facilities/425"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://tripto.jp/facilities/425"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://tripto.jp/facilities/425"}}},

    "168": {"name": "湯屋　やまざくら",
            "reason": "「プライベートサウナと水風呂付きで、“ととのう”を体感してみてください」→coldbath=bath、「Wi-Fi接続」。sauna_hours は「チェックイン～23:30」がサウナ専用か温泉全体かが不明瞭なため入れない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://hakoneyamazakura.com/onsen.html"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hakoneyamazakura.com/onsen.html"}}},

    "181": {"name": "GLAMDAY STYLE HOTEL SUITE 川ノ音",
            "reason": "トラッキングパラメータなしの正規URLで確認。「プライベートサウナ」「バスルームに併設」→sauna_type=indoor、「ご宿泊人数 2～6名」（SARASARA・SOUSOU両棟共通）、「隣接のテラスでは、自然の風を感じる外気浴で」「Wi-Fi 有」。**stove は入れない**: WebSearch要約が「Harviaストーブ・100℃近く」と述べたが記事本文2本を直接取得しても裏付けが取れず、「薪ストーブ」の語はテラスの暖炉についての記述だった（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://gs-hotelsuite.jp/kawanone/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://gs-hotelsuite.jp/kawanone/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://gs-hotelsuite.jp/kawanone/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://gs-hotelsuite.jp/kawanone/"}}},

    "182": {"name": "The Aurora Chalet",
            "reason": "公式サイトが存在しない（jadehotelgroup.com はリンク集のみ）ためOTAを出典とする。住所「北安曇郡白馬村北城836-141」で照合済み。「当施設で大好評のサウナはロウリュウ式で薪ストーブを使用、オールシーズンご利用可能です」→stove=wood / loyly=yes、「ペット 不可」「無料WiFi」。サウナイキタイで独立2回の検索が90℃・17℃で一致した。capacity は一休「定員 1名～9名」がOTA上限表記に該当し、かつ AURORA-1／AURORA-2 が1リスティングに混在するため入れない（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "sauna_temp": {"v": 90, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "water_temp": {"v": "t1518", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/vacation/00051575/"}}},

    "183": {"name": "Hakuba Amber Resort",
            "reason": "住所「北安曇郡白馬村北城830-90」で照合済み。「サウナ あり」「1匹につき5,200円の追加料金」→pet_ok=yes、「wi-fiが利用可能です」。capacity は一休「定員 1名～9名」（3LDK）「1名～6名」（2LDK）でOTA上限表記の疑いがあり変更しない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051318/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051318/"}}},

    "187": {"name": "GREENSEED軽井沢",
            "reason": "サウナ利用規約PDFに「水を一気にかけると、水が蒸発せずに電気ストーブにかかり、故障の原因となります」→stove=electric、「サウナストーンへの水かけ（ロウリュ）については、1回あたり柄杓1杯～2杯程度でお願いいたします」→loyly=yes、「ご利用人数 最大6名」（全6タイプ共通）（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://greenseed-villa.com/rooms/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://greenseed-villa.com/rooms/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://greenseed-villa.com/rooms/"}}},

    "192": {"name": "ポーラーハウスカナディアン南軽井沢1",
            "reason": "住所「北佐久郡軽井沢町発地336-1」で照合し、酷似名の「ポーラーハウス南軽井沢1」（群馬県下仁田町）と区別した。「1階サウナ室…本格3人用ナチュラルサウナ」→sauna_type=indoor / sauna_cap=3、「外気浴では南軽井沢の澄んだ空気を胸いっぱいに吸い込みます」「Wi-Fi完備でワーケーションも可能」。**stove と coldbath は入れない**: レビュー文の「薪の香りに包まれながら」から wood と即断しかけたが、運営元ブログが自社サウナを「ロウリュ（湿式）」と「ナチュラル（遠赤外線）」に分類しており本施設は後者。遠赤外線は wood/electric/gas のいずれにも当てはまらない。同ブログは「ナチュラルサウナの後は水風呂でなく25～30℃のぬるま湯やシャワーを推奨」とも明記している。「薪の香り」はログハウスの建材由来とみられる（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/カナディアン南軽井沢1"},
                         "sauna_cap": {"v": 3, "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/カナディアン南軽井沢1"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/カナディアン南軽井沢1"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/カナディアン南軽井沢1"}}},

    "202": {"name": "キュレーション熱海須藤水園",
            "reason": "**sauna_exists=no。** 一休の設備欄が○✕形式で「サウナ：× なし」と明示している。公式（curationhotels.com）にもサウナの記載が一切ない。同ブランドの桃山雅苑も同じく✕で、桃乃八庵も公式にサウナの記載がない。公式「寝室2部屋（定員最大4名）」→capacity=4（一休は「定員1名～6名」と食い違うため公式を優先）、「本施設は、ペットの同伴は禁止とさせていただいております」「Wi-Fi環境あり」「IHコンロ」（2026-08確認）",
            "set_villa": {"capacity": "4"},
            "set_spec": {
                         "sauna_exists": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051777/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051777/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051777/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051777/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051777/"}}},

    "203": {"name": "キュレーション熱海桃山雅苑",
            "reason": "**sauna_exists=no。** 一休の設備欄が○✕形式で「× サウナ」と明示。公式にもサウナの記載がない。「最大8名で宿泊ができ」（公式）と「定員 1名～8名」（一休）の2ソースが一致、「Wi-Fi」「ポータブルIHコンロ」（2026-08確認）",
            "set_spec": {
                         "sauna_exists": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051776/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051776/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051776/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051776/"}}},
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
