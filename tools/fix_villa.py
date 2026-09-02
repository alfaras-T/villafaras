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
    "74": {"name": "SANU 2nd Home 八ヶ岳2nd",
            "reason": "出典なし8項目のうち7項目が一致した。公式のサウナ設備リスト「ロウリュ用バケツ／柄杓」→loyly、「水風呂・ととのい椅子」の見出しでテラス設置→coldbath / outdoor_rest、公式FAQ「最大定員は4名」＋BEE棟ページ「最大収容人数4名」→capacity=4、一休でサウナ・ペット同伴が部屋限定である旨→sauna_exists=room、一休のレビューとテーマタグ「バレルサウナを楽しめる宿」→sauna_type=barrel、一休「ペット可」→pet_ok。**stove=gas だけ根拠が見当たらない**: 公式・一休のいずれにもサウナの熱源記載が無く、BEE棟の基本設備にある「ペレットストーブ」はエアコン・洗濯乾燥機と並ぶ居室の暖房設備。以前 WebSearch 経由で「ONE SAUNA製ガスストーブ」との情報を得ていたが公式では確認できない（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "room", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/architectures/sanucabinbee"}}},

    "102": {"name": "SAUNEA白州",
            "reason": "**coldbath を bath から pool に訂正する。** 公式が設備名を「水風呂プール」と表記し、「じっくりと汗をかき屋外プールにさっと浸かる」「広々とした水風呂は爆快感抜群！」と書いている。一休の構造化データにも「屋外プール／プールサイズ 長さ3m×幅2m／水深50-60cm／プール形状：方形」とあり、独立した浴槽は無い。2026-08 に追加した pool（プール兼用）の定義に合致する。他7項目は一致した: 公式「アウトドアキューブ型サウナ」→sauna_type=hut（一休も「一般的なバレルサウナより広い」とバレルでないことを裏付け）、「好きな温度設定でロウリュもし放題」→loyly、外気浴用アウトドアチェア6脚→outdoor_rest、「グリル付きIHコンロ2口」→kitchen_type=ih、「最大6名宿泊可能」→capacity=6、pet_ok / wifi も公式に記載（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://hakushu.saunea.jp"}}},

    "170": {"name": "Six on the Beach TORAMII -Enoshima-",
            "reason": "出典なし6項目のうち5項目が一致した。**公式の改装告知が sauna_type と stove を同時に確定させている**: 2024年7月にテント式から「オリジナル小屋」＋「電気ストーブ」へ切り替えた旨が明記されており、サウナイキタイの情報（テント・薪）は改装前のまま古い。「最大12名様まで」→capacity=12、ロウリュ利用可の記載→loyly、一棟貸切の敷地内常設→sauna_exists。**pet_ok は不明**: 公式トップにペットの記載が無く、設備マニュアルPDFは画像ベースで読み取れなかった（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/enoshima/"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/enoshima/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/enoshima/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/enoshima/"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/enoshima/"}}},

    "195": {"name": "Earthboat Kurohime",
            "reason": "**capacity を 3 から 6 に訂正する。** 公式の基本情報欄に「定員 3~6名」と範囲で書かれており、客室説明は「プライベート薪サウナを備えた定員3名までの客室」。客室タイプに Group Plan があり、2棟連結利用で6名になる。**公式が施設全体の数字を出しているのでそれを採る**（「範囲は上限を採る」規約）。既存の3は単棟の数字。同ブランドの id=122 Nasu は公式が「定員 3名」で範囲表記が無いため3のままでよく、**Earthboat は拠点ごとに違う**。他4項目は一致: 柄杓の備品記載→loyly、設備欄「水風呂」→coldbath、インフィニティチェア→outdoor_rest、「種類・大きさ・頭数の制限なし」→pet_ok。**sauna_type は入れない**: 客室詳細ページの「客棟タイプ」が英語で「Hut」と書かれているが、これは客棟（宿泊する棟）の型式であってサウナ本体の形式ではない（2026-09確認）",
            "set_villa": {"capacity": "6"},
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"}}},

    "214": {"name": "マイグレICE",
            "reason": "公式に「テントサウナ」→sauna_type=tent、「水風呂」（湧水利用）→coldbath、「定員5名」→capacity、ロウリュ・Wi-Fi も記載。**stove=electric は今回も確定できない**: 「Harviaのサウナストーブ」というブランド名のみで型番も方式欄も無い（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"},
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"},
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ice"}}},

    "219": {"name": "マイグレIKKI",
            "reason": "公式に「サウナ小屋」→sauna_type=hut、「水風呂」→coldbath、「定員10名」→capacity、ロウリュ・Wi-Fi も記載。**stove=electric は確定できない**: 「Harviaのサウナストーブ」＋「リモコンで温度調節可能」で、リモコン制御は電気式を示唆するが熱源の明言ではない（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"},
                         "capacity": {"v": 10, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/ikki"}}},

    "220": {"name": "マイグレKENKEN",
            "reason": "公式に「サウナ小屋」→sauna_type=hut、「水風呂」→coldbath、「定員5名」→capacity、ロウリュ・Wi-Fi も記載。**stove=electric は確定できない**（id=219 と同じく「リモコンで温度調節」の付帯情報のみ）（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"},
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kenken"}}},

    "221": {"name": "マイグレYEBISU",
            "reason": "**capacity=9 の裏付けが取れた。** 公式に「定員9名」と明記されており、CLAUDE.md が「9が正しい施設」として挙げていた1件。「水風呂」（直径1.4mの専用浴槽）→coldbath、ロウリュ・Wi-Fi も記載。**sauna_type=indoor を新規に記録**: B1Fの部屋一覧に「サウナルーム」「ミストサウナルーム」とあり、他のマイグレ施設のような屋外の「サウナ小屋」ではない。**stove=electric は確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"},
                         "capacity": {"v": 9, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/yebisu"}}},

    "222": {"name": "マイグレ海の声",
            "reason": "公式にウッドデッキの「サウナ小屋」→sauna_type=hut（浴室内に別系統のミストサウナも併設）、「水風呂」がジャグジーとは別項目→coldbath、「定員7名」→capacity、ロウリュ・Wi-Fi も記載。**stove=electric は確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"},
                         "capacity": {"v": 7, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/uminokoe"}}},

    "223": {"name": "マイグレケニーズハウス",
            "reason": "公式に「屋内に設けたサウナルーム」→sauna_type=indoor、「水風呂」→coldbath、「定員16名」→capacity（他施設より突出しているが3寝室205㎡の大型一棟貸しで裏付けあり）、ロウリュ・Wi-Fi も記載。**stove=electric は確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"},
                         "capacity": {"v": 16, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/kennys"}}},

    "224": {"name": "マイグレchillax",
            "reason": "公式に「マイグレ初、屋内に設けた」サウナルーム→sauna_type=indoor、「水風呂」→coldbath、「定員7名」→capacity、ロウリュ・Wi-Fi も記載。**stove=electric は確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"},
                         "capacity": {"v": 7, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/chillax"}}},

    "226": {"name": "マイグレアトリエ",
            "reason": "公式に「サウナ小屋」→sauna_type=hut、「定員6名」→capacity、ロウリュ・Wi-Fi も記載。**coldbath=bath を新規に記録**（「水風呂」明記）。**stove=electric は確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/atelier"}}},

    "227": {"name": "マイグレA5",
            "reason": "**capacity を 6 から 5 に訂正する。** 公式ページを直接取得したところ、**上部の構造化表示は「定員 5名」**で、ベッド構成も「洋寝室①：セミダブルベッド2台／洋寝室②：シングルベッド3台」＝5床と一致する。本文の「寝室は2部屋をご用意しました。最大6名様までご宿泊いただけます。」は**隣の id=226 アトリエ（定員6）と一字一句同じ定型文**で、他8施設では上部表示と本文が一致しているため、この施設だけコピペの変更漏れとみられる。**id=215 マイグレテラスで公式の構造化表示が紹介文に勝ったのと同じ構図。** 他の項目は一致: 「サウナ小屋」→sauna_type=hut、ロウリュ・Wi-Fi。**stove=electric は確定できない**（2026-09確認）",
            "set_villa": {"capacity": "5"},
            "set_spec": {
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/a-five"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/a-five"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/a-five"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/a-five"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/a-five"}}},
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
