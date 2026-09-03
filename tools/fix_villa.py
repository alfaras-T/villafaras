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
    "5": {"name": "＆SUN Hung five",
            "reason": "施設自身の予約サイトのプラン名「【直前割】＜2名様まで同一料金＞ 宿泊日直前の特別プラン（最大5名様）」→capacity=5（一休の「定員1名〜5名」はOTA表記なので根拠にせず、施設固有の記述を採った）。pet_ok=yes は公式「小型犬一頭のみ宿泊可能」＋一休「○ ペット可」、wifi=yes は公式「Wi-Fiあり」＋一休の2ソース。住所は公式「千葉県南房総市久枝1274-7」で一致（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/sun-hungfive/0/plan"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/sun-hungfive/0/plan"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://reserve.489ban.net/client/sun-hungfive/0/plan"}}},

    "13": {"name": "Ocean's Terrace TORAMII",
            "reason": "公式「ヒノキのサウナ小屋」→sauna_type=hut、「80〜90度まで自動上昇する電気式」→stove=electric（**サウナ自体を修飾する記述**なので確定できる）。pet_ok=yes は一休 00050140「○ ペット可」「ワンちゃんが、遊べるのは庭とウッドデッキのみです」（公式にはペットの記載が無い）（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/oceans-terrace-toramii/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/oceans-terrace-toramii/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/oceans-terrace-toramii/"}}},

    "54": {"name": "Zekkei stay ISUMI cabin",
            "reason": "一休「薪サウナを完備しており、セルフロウリュも楽しめます。」→loyly=yes、同一文「サウナ室を出ると芝生のお庭にはこだわりの打たせ水シャワーとタライの水風呂をご用意。」→coldbath=bath（浴槽兼用ではなく専用の水風呂）。**さらに同じ文から stove=wood を新規記録する**: 「薪サウナを完備」はサウナ自体を修飾しており確定基準を満たす。**この施設は 2026-09 に公式の安全注意にあった「薪ストーブ」を居室設備と判断して stove を削除した施設**だが、今回は一休がサウナ自体を「薪サウナ」と書いており根拠が変わった。**同じページに両方が書かれている**: 「薪サウナを完備し、薪をくべて炎を眺めながらセルフロウリュが楽しめ」（サウナ本体）と「また薪ストーブもございますので火傷には十分ご注意ください。」（客室の暖房）。**居室に薪ストーブがあることは薪サウナの否定にならない。** あわせて「サウナ室は2～3人で使用可能」から sauna_cap=3 を記録する（範囲は上限を採る）。**capacity=6 は不明のまま**: 公式（chillnn）にも一休にも定員の数字が無い（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051913/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051913/"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051913/"},
                         "sauna_cap": {"v": 3, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051913/"}}},

    "63": {"name": "Dear Wan Spa Garden",
            "reason": "一休「■長柄カルナの湯（男性：半露天風呂／女性：内湯） 男女ともにサウナ完備｜ご利用時間 11:00～17:00」→sauna_exists=shared（時間制の共用大浴場で客室サウナではない）。pet_ok=yes は公式「愛犬とともに」＋一休「○ Pet-friendly」「可（ワクチン接種証明書が必要）」。**capacity=3 は不明のまま**: 一休の「Capacity: 1-3 guests per villa」はOTAの範囲表記で根拠にできず、公式にも明確な最大人数の記載が無い（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "shared", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052128/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052128/"}}},

    "75": {"name": "SANU 2nd Home 八ヶ岳3rd",
            "reason": "SANU公式の拠点一覧「八ヶ岳3rd／MOSS／4名／サウナ / ドッグフレンドリー」→capacity=4（一休の「1名～4名」はOTA範囲表記なので不採用）。coldbath=bath は MOSS型記事「テラスに水風呂とととのい椅子を備えています」（**八ヶ岳3rd は sauna-moss 記事の名指しリストに含まれることを確認済み**：北軽井沢2nd／八ヶ岳3rd／白馬1st／河口湖2nd／南アルプス1st）。pet_ok=yes は一休 00052073「○ ペット可」（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/yatsugatake"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/yatsugatake"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/yatsugatake"}}},

    "106": {"name": "郷音 -G.O.A.T.- The Summit Club",
            "reason": "**capacity=16 の根拠が見つかった。** 運営会社（株式会社ReZARD）のプレスリリースに「施設内には、メインベッドルーム1室、サブベッドルーム3室を備え、キングベッド1台、ダブルベッド10台を設置。最大16名まで快適にご宿泊いただける設計となっており」と明記。**公式サイトの /rooms ページ自体には「16」という数字が存在せず、AI要約が『5棟×4名＝16』という本文にない計算を提示していた**ため、プレスリリースで裏を取った。coldbath=bath は公式「水風呂、ジャグジー、ロウリュウセット、アロマ」（水風呂とジャグジーが別設備）。pet_ok=yes は「G棟、O棟、Y棟はペット可」で**5棟中3棟限定**（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 16, "src": "desk", "at": "2026-09",
                                        "url": "https://prtimes.jp/main/html/rd/p/000000003.000164884.html"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://prtimes.jp/main/html/rd/p/000000003.000164884.html"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://prtimes.jp/main/html/rd/p/000000003.000164884.html"}}},

    "118": {"name": "SANU 2nd Home 那須1st",
            "reason": "**addr が不完全だった。「栃木県那須郡那須町高久乙449」→「栃木県那須郡那須町高久乙3370-449」。** SANU社のプレスリリースと一休がどちらも「高久乙3370-449」で、番地の「3370-」が欠落していた。国土地理院のジオコーディングでも訂正案だけが「栃木県那須町高久乙３３７０番地」と番地まで解決し、保存済み座標との距離が 1.77km から 0.89km に縮まる。capacity=4 は公式の拠点一覧「那須1st／4名」、pet_ok=yes は一休「可（犬以外のペット（猫や鳥、他）は同伴いただけません）」。**sauna_type=barrel は不明のまま**: 那須1st は BEE型で sauna-moss 記事の対象拠点に含まれず、公式エリアページにも「サウナ / ドッグフレンドリー」の記載のみでバレル型の明記が無い（2026-09確認）",
            "set_villa": {"addr": "栃木県那須郡那須町高久乙3370-449"},
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/nasu"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/nasu"}}},

    "135": {"name": "ASNOVA RESORT FOLQ HAKONE GORA",
            "reason": "公式ルームページ「定員 各室４名まで（2名までは同一料金で1名追加ごとに定価10,000円／人が追加となります。）」→capacity=4（一休の「1名～4名」はOTA範囲表記なので不採用）。loyly=yes は公式「セルフロウリュもできる個室サウナ」、pet_ok=yes は公式「ご同伴いただけます」＋一休「可」最大3頭（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://asnova-resort.com/folq-gora/room/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://asnova-resort.com/folq-gora/room/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://asnova-resort.com/folq-gora/room/"}}},

    "146": {"name": "TIMeSCAPE -hakone-",
            "reason": "公式の客室概要「定員：8名」（ベッド120cm幅×6台と併記）→capacity=8、トップ「檜のサウナ」＋FAQ「ヒノキ香るサウナ」→sauna_exists=yes。**loyly=yes は不明のまま**: 公式のトップ・FAQ・stay の全ページで「ロウリュ」の語自体が見つからず、一休にも掲載が無い（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://timescape-hakone.jp/stay/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://timescape-hakone.jp/stay/"}}},

    "162": {"name": "プライベートヴィラ愛川",
            "reason": "公式「セルフロウリュも可能なバレルサウナとジャグジーを設置」→sauna_exists=yes / sauna_type=barrel（一文で両方が確定する）。pet_ok=yes は公式「ペット：大型、中型、小型 頭数制限なし」。一休には掲載が無い（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://withthedogs.jp/villa"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://withthedogs.jp/villa"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://withthedogs.jp/villa"}}},

    "188": {"name": "COCO VILLA 軽井沢",
            "reason": "公式「3Dプリンターで制作したオリジナルのサウナ（電気式サウナ）」→sauna_exists=yes、「水風呂として専用で設置」→coldbath=bath（浴槽兼用ではない）、「ととのいスペース」「ととのい用チェア」→outdoor_rest=yes。**「サウナ用ハット」の誤用は無かった**: 公式の設備一覧に「サウナまわり：サウナ用ハット／サウナ用マット／サウナ用アロマ」とあるが、既存の sauna_type=hut の根拠は「敷地内に設置」という別棟である旨の記述のほうだった（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/karuizawa/"}}},

    "198": {"name": "T&A Resort&Sauna KARUIZAWA",
            "reason": "公式サイトも一休も存在しない施設。Booking.com のホスト説明文「T&A Resort&Sauna KARUIZAWAでの滞在中はサウナを利用できます。」「◎ 電気サウナ 料金：5,500円 利用時間：22:00まで」→sauna_exists=yes（既存の stove=electric の裏付けにもなる）。pet_ok=yes は「ペット宿泊可。追加料金あり。」「小型犬・中型犬 最大2頭までご宿泊可能です。」。**capacity=11 は変更しない**: 同一ページ内でホスト説明文が「ベッドルーム3室(12名可)」、部屋タイプ選択欄が「× 11」と食い違うと報告されたが、**Booking.com をこちらで直接取得すると本文が空で返り自分では確認できなかった。**既存の11は選択欄の数字と一致しており、どちらが正しいか決められない（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.booking.com/hotel/jp/t-amp-a-resort-amp-sauna-karuizawa.ja.html"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.booking.com/hotel/jp/t-amp-a-resort-amp-sauna-karuizawa.ja.html"}}},

    "206": {"name": "オーシャンビュー熱海自然楼",
            "reason": "**capacity を 10 から 8 に訂正し、addr の字名も直す。** 公式を直接取得して確認した。住所は「〒413-0101 静岡県熱海市上多賀**字藤広地**1065-83（熱海自然郷 初島台92）」で、DBの「字藤河内」は誤り（番地1065-83・施設名・写真は一致するので同一施設）。定員は「8名」と明記され、寝具構成「布団×3・布団×3・シングル×2」＝8とも内部で整合する。pet_ok=no は「本施設は、ペットの同伴は禁止とさせていただいております。」、wifi=yes は「Wi-Fi環境あり」。**備え付け家電欄の「電気ストーブ」はテレビ・電子レンジ・冷凍冷蔵庫・冷暖房エアコンと並ぶ居室用の暖房器具**で、この施設にはサウナ自体の記載が一度も無い（2026-09確認）",
            "set_villa": {"capacity": "8", "addr": "静岡県熱海市上多賀字藤広地1065-83"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamishizenrou/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamishizenrou/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.resolstay.jp/details/atamishizenrou/"}}},
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
