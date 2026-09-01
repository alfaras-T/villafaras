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
    "168": {"name": "湯屋　やまざくら",
            "reason": "ota の一休URLに広告トラッキングパラメータ（?adcid=&adfid=…&ikCo=googlehp）が付いていたので正規URLに直す。2026-08 の ota 全件走査で挙げた品質問題の類型（2件目の訂正）（2026-09確認）",
            "set_villa": {"ikyu": "https://www.ikyu.com/00031190/"}},

    "165": {"name": "箱根懐來",
            "reason": "一休の基本情報「ペット 不可」。既存値も裏付けが取れた: sauna_exists=yes は公式「プライベートサウナ」＋一休「サウナ あり」、capacity=4 は公式「2名様〜4名様まで1棟貸切でのご利用が可能です。」＋一休「定員 2名〜4名」の2ソース。**loyly は入れない**: 公式「ロウリュも堪能できます」はセルフ／オートの区別が無い。**kitchen_type も入れない**: 「システムキッチン」のみで、しかも「火器の使用や食材の持ち込みによる調理はご遠慮いただいております」という制約がある（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052195/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052195/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052195/"}}},

    "171": {"name": "Noёl HAKONE GENSEN",
            "reason": "**wifi を記録する。前回（W6-2）は公式の「50台以上の同時接続可能なルーターもご用意しております」だけではWi-Fiの明記ではないとして見送ったが、一休に「wi-fiが利用可能です」があった。**（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051638/"}}},

    "178": {"name": "SANU 2nd Home 軽井沢2nd",
            "reason": "**ブランド内の取り違えを回避した。** 公式マガジンのMOSS型記事は対象拠点として「北軽井沢2nd／八ヶ岳3rd／白馬1st／河口湖2nd／南アルプス1st」を名指ししているが、**「軽井沢2nd」は含まれていない。「北軽井沢2nd」と「軽井沢2nd」は別拠点**（sa-nu.com のエリアページも /areas/karuizawa と /areas/kitakaruizawa で分かれている）。したがってロウリュ・水風呂・外気浴の詳細は流用していない。wifi は一休。pet_ok=yes は拠点別ページ「愛犬同伴：2棟」で**一部棟のみ**と判明（一休は設備欄「× ペット可」と基本情報「ペット 可」が内部で食い違う）。**capacity=4 は要検討**: MOSS Medium「4名」／MOSS Large「最大宿泊人数 6名」と拠点内に2種類の棟タイプがある（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/list/mossm_karuizawa2nd"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/list/mossm_karuizawa2nd"}}},

    "180": {"name": "GLAMDAY STYLE HOTEL SUITE 山ノ麓",
            "reason": "**stove=wood（2026-07・出典なし）を削除する。居室ストーブとの混同の7件目。** 公式を直接取得したところ「憧れの薪ストーブ」という見出しの下に「軽井沢の冬を彩るのは、リビングルームにしつらえた薪ストーブ。…お部屋全体を温めるストーブで、温かな軽井沢の冬をお過ごしください。」とあり、**部屋全体の暖房**と明記されている。一方サウナの説明は「バスルームには、プライベートサウナをしつらえております。」までで**熱源の記載が一切ない**。一休も「冬は薪ストーブを囲む室内として」と居室の文脈で書いている。同じ「バスルームには」からsauna_type=indoor、「隣接のテラスでは、自然の風を感じる外気浴で体温を整えながら」からoutdoor_rest=yes。pet_ok=yes は既存値だが**CEDAR棟限定**（他のWALNUT・BIRCHにはペットの記述が無い）（2026-09確認）",
            "remove_spec": ["stove"],
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://gs-hotelsuite.jp/yamanofumoto/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://gs-hotelsuite.jp/yamanofumoto/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://gs-hotelsuite.jp/yamanofumoto/"}}},

    "186": {"name": "Lakeside villa SUI HAKUBA",
            "reason": "一休の基本情報「ペット：不可」。**stove は入れない**: 公式「各ヴィラには、4人がゆったりと座れ…プライベートサウナをご用意しています。お好みに応じて温度も調整できます。」は温度調整の話で熱源ではない。**outdoor_rest も入れない**: 一休の口コミに「リラックスチェアを湖のそばまで持っていって外気浴をしたのですが」とあるが施設側の案内ではない。サウナイキタイに掲載なし（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052430/"}}},

    "199": {"name": "北軽井沢 貸別荘 FARMSIDE",
            "reason": "公式の設備一覧「・Wi-Fi・薪ストーブ・サウナ・エアコン（冷暖房）・シャワー・トイレ・ダイニングテーブル・洗濯機」→wifi=yes、「定員：1〜4名」で既存の capacity=4 も裏付け。**この設備一覧は「薪ストーブ」と「サウナ」を並列の別項目として書いており、居室ストーブ混同のパターンに該当し得る書き方**だが、既存の stove=electric はこの一覧ではなくサウナイキタイを出典にしているため混同は起きていない（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://newsite.kitakaruizawafarmstay.com/log-house/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://newsite.kitakaruizawafarmstay.com/log-house/"}}},

    "208": {"name": "パノーラ熱海桜沢",
            "reason": "**sauna_exists を yes から room に訂正する。** 公式を直接取得したところ部屋タイプが2種類あり、サウナがあるのは2Fタイプだけだった。「2Fタイプはドライサウナ付きで、より健康的なリゾートライフが満喫できます。」「2階浴室には美容・リラックス効果が期待できる低温サウナ付き。」に対し、1Fタイプは「温泉と海の眺望が楽しめる大浴槽」でサウナの記載が無い。「2階浴室には…サウナ付き」から sauna_type=indoor。既存の capacity=6 は「定員 6名」で裏付け、pet_ok=yes も「A(下階)のみペット同伴可」「小型犬（体重8kg未満）、猫（室内飼い） 合計2匹まで」で確認したが**下階限定**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "room", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/panoraatamisakurazawa/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/panoraatamisakurazawa/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/panoraatamisakurazawa/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/panoraatamisakurazawa/"}}},

    "230": {"name": "WEAZER西伊豆 廻",
            "reason": "公式FAQ「申し訳ございませんが、ペットをお連れのお客様はご宿泊いただけません。」＋一休 00003449「ペット 不可」→pet_ok=no。既存値も裏付けが取れた: 公式FAQ「WEAZER 廻のお部屋には客室内にサウナ(定員2名・95℃)がございます。」→sauna_exists=yes（既存の sauna_cap=2 / sauna_temp=95 とも整合）、公式予約ページ「WEAZER 廻 定員4名：大人4名まで・子ども4名まで」→capacity=4。**他媒体に「最大5名」「1 to 3」という異なる数値があるが、施設自身の予約サイトを採る。** **stove は入れない**: 施設全体が「客室内は電気や水道、ガスに接続しておらず、電気は太陽光発電」というオフグリッド仕様でガス非接続・薪の記載も無いため電気式の可能性は高いが、サウナの熱源を明示した文言が無い（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.chillnn.com/ja/1836d2246923a9/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.chillnn.com/ja/1836d2246923a9/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.chillnn.com/ja/1836d2246923a9/"}}},

    "237": {"name": "Tiny Base The Irita-hama",
            "reason": "公式「IHコンロや、調理器具、カトラリー各種」→kitchen_type=ih。既存値も裏付けが取れた: 公式「The River TRAILER/The Valley/The Irita-hamaは電気式サウナストーブです」と**拠点を名指し**しており sauna_exists=yes、予約サイト「The Irita-hama【…〈最大収容人数：8名様〉】」→capacity=8、「ペット同伴 OK」「当施設はTiny Base初の愛犬対応施設です！」＋楽天「最大3頭まで」→pet_ok=yes。**sauna_type は入れない**: 楽天の「フィンランド式サウナストーブ（HARVIA社・電気式）」の「フィンランド式」は様式の呼称で構造ではない（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/tinybase-irita-hama/0/plan"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/tinybase-irita-hama/0/plan"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/tinybase-irita-hama/0/plan"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/tinybase-irita-hama/0/plan"}}},

    "240": {"name": "Wellリゾート富士",
            "reason": "一休「国産ヒノキバレルサウナ付き」→sauna_type=barrel。既存値も裏付け: 公式FAQ「ございます。※水風呂はございません」→sauna_exists=yes（既存の coldbath=none とも整合し、しかもこれは明示的な否定文）。**capacity=3 は要検証**: 一休は「客室数 2室」で別館「定員 1名〜2名」・ヴィラ「定員 1名〜5名」の2タイプがあり、3はどちらとも一致しない（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051982/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051982/"}}},

    "277": {"name": "No.12 Kashima Fan Zone",
            "reason": "**coldbath を bath から pool に訂正する。** サウナイキタイの施設情報欄に「地下水の掛け流しです。**屋外用のプールを水風呂として活用しております**。」（水深110〜140cm・水温20℃）とあり、2026-08 に追加した pool（プール兼用）の定義に合致する。**あわせて sauna_type=barrel を削除する。** 共用サウナは3種類（「騒」大型電気ドライサウナ／「静・黙」室内サウナ／「動」スクールバス改造サウナ）で**いずれもバレルではない**。さらに公式 /stay/ に「全棟個室サウナ…付属しております」とあり宿泊棟にも別の個室サウナが併存する。1項目に代表させられない典型例で、CLAUDE.md が DB構造の限界に挙げている施設。「●外気浴 イス: 12席 寝転べるイス(フルフラット可): 8席 ベンチ: 20席」→outdoor_rest=yes。既存の capacity=6 も公式「離れの小上がりに布団を敷くことで最大6名の宿泊が可能です。」で裏付け。**loyly は入れない**: 「セルフロウリュ お好みでお楽しみ下さい」とあるが共用3種のうち「動」はロウリュ不可とレビューにあり全サウナ共通ではない（2026-09確認）",
            "remove_spec": ["sauna_type"],
            "set_spec": {
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/87241"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/87241"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/87241"}}},
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
