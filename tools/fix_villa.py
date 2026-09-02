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
    "2": {"name": "古民家宿るうふ 波之家",
            "reason": "**coldbath=bath を削除する。サウナ提供終了に伴う消し忘れ。** 公式に「テントサウナにつきまして、2026年1月16日をもってご利用を終了いたしました。」とあり sauna_exists=no を記録済みだが、水風呂の値が残っていた。公式のお風呂設備は「浴槽、シャワー」のみで水風呂の記載が無い。**validate.py の SAUNA_FIELDS に coldbath が入っていなかったため検出できていなかった**（今回widenして検出できるようにした）。他は一致: 公式「定員 ： 8名（ダブルベッド1台、シングルベッド2台、布団4組）」→capacity=8、「わんちゃん用アメニティ：ケージ（幅135cm×奥行108cm×高さ72cm、25㎏まで）」＋一休「○ ペット可」→pet_ok=yes。**kitchen_type=gas を新規記録**（公式「調理器具：…ガスコンロ…」）（2026-09確認）",
            "remove_spec": ["coldbath"],
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/naminoie/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/naminoie/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/naminoie/"}}},

    "3": {"name": "古民家宿るうふ 遊之家",
            "reason": "出典なし5項目すべて一致した。公式「半露天の広い浴室でバレルサウナと檜風呂をお楽しみいただけます。」→sauna_type=barrel、「お風呂 - 設備：人工温泉露天風呂、サウナ、水風呂、シャワー」→coldbath=bath（水風呂は露天風呂と別立て）、「水風呂と杉皮の壁が囲むデッキでリラックス。」→outdoor_rest、「調理器具：…ガスコンロ…」→kitchen_type=gas、「定員：８名」→capacity。**新規に pet_ok=no**（一休「ペット 不可」「× ペット可」）と **loyly=yes**（公式「ロウリュでじっくり汗を引き出し」＋一休「セルフロウリュもお楽しみいただけます」）も記録する。**同ブランドでも棟ごとに違うことの再確認**: id=0 揺之家は薪ストーブの語すら無く、id=4 鴨川919 は「薪ストーブのサウナ」と明記、この id=3 はバレルサウナだった（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yunoie"}}},

    "89": {"name": "景雅 奥河口湖",
            "reason": "coldbath / outdoor_rest / wifi の3項目が一致した。公式「サウナでは、水風呂、外気浴コーナーで『整う』時間を、ぜひお過ごしください。」「インターネット環境 フリーWi-Fi」。**新規に sauna_type=indoor**（客室設備が「キッチン、ダイニング、リビング、ベッドルーム、シャワールーム、サウナ、露天風呂、トイレ、水盤テラス」と室内設備の一部として並んでいる）。**capacity=5 は変更しない**: 公式は「客室数 2室」「最大収容人数 8名（スイートヴィラ5名×1室／スタンダードヴィラ3名×1室）」と書いており8への訂正が提案されたが、**同じ運営（global-stays.jp）の id=90 totonoco は「最大収容人数：18名（プライベートヴィラ3名×6室）」に対しDBは per-unit の 3 を採っている。** 合算しない扱いで揃える。加えて公式に2室をまとめて予約できる旨の記載が無い。既存の5はスイートヴィラの数字（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/keiga/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/keiga/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/keiga/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/keiga/"}}},

    "172": {"name": "Oyado S",
            "reason": "**capacity=12 は変更しない。提案の根拠が別施設だった。** じゃらん yad347487 を直接開いたところ、そこの「OYADO S」は**神奈川県鎌倉市大町1丁目14番3号**の施設で、DBの id=172（神奈川県足柄下郡箱根町元箱根93-143、公式は oyados-ashinoko＝芦ノ湖）とは別物。**同名の別施設という既知の罠**にあたる。同じ理由で wifi も採用しない。公式（chillnn）から確認できた4項目は一致: 「素泊まりプラン。犬猫OKのサウナ付き一棟貸しお宿。」→sauna_exists / pet_ok、注意事項「サウナストーブに大量の水をかけないでください…必ず柄杓を使って10〜15分毎に柄杓1〜2杯を優しくかけてください。」→loyly=yes（セルフ）、「水風呂の水は、使用後は止めてください。」→coldbath=bath（DBの紹介文「水温10〜18度のチラー付き水風呂」とも整合）（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://oyados-ashinoko.booking.chillnn.com/ja/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://oyados-ashinoko.booking.chillnn.com/ja/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://oyados-ashinoko.booking.chillnn.com/ja/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://oyados-ashinoko.booking.chillnn.com/ja/"}}},

    "193": {"name": "SAUNA FOREST CABIN 軽井沢御代田",
            "reason": "**capacity を 9 から 10 に訂正する。** 施設自身の予約エンジン（airhost）の物件詳細に「寝室3部屋、ベット7台 **最大収容人数10名**」と明記されている（ZEN-ASOBI棟。MORI-ASOBI棟も同一仕様と公式に明記）。既存の9は一休の「定員 1名～9名」＝OTA上限の遺物。2棟同時利用なら「ベッド14台、最大収容人数20名まで」。他は一致: 一休「サウナ あり」＋公式FAQ→sauna_exists、公式FAQ「Wi-Fi完備しております。」→wifi。**新規に loyly=yes / pet_ok=no**。**sauna_type は不明のまま**: WebSearchの要約が「専用のバレルサウナ」と本施設に紐付けたが、記事本文を直接確認するとこれは**別施設「ニコトレハウス北軽井沢」の説明文**だった（別施設混入の実例）（2026-09確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-09",
                                        "url": "https://airhost2048.airhost.co/ja/houses/291312"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://airhost2048.airhost.co/ja/houses/291312"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://airhost2048.airhost.co/ja/houses/291312"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://airhost2048.airhost.co/ja/houses/291312"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://airhost2048.airhost.co/ja/houses/291312"}}},

    "216": {"name": "マイグレ天",
            "reason": "**index.html と spec-data.js の capacity 不一致（既知の未決着2件のうち1件）が解消した。** 公式トップに大きく「定員 7名」と明記されており、spec-data.js の7が正しく index.html の5が誤り。他は一致: 公式「ウッドデッキテラスにはオーナーのこだわりが詰まったサウナと露天風呂。」→sauna_exists、「サウナを出ると、オーバーヘッドシャワーにスタイリッシュな猫足のバスタブ。伊豆の自然を感じながら『ととのい』を。」→outdoor_rest、「Wi-Fi 完備」→wifi。**stove は今回も確定できない**（Harviaのブランド名のみ）（2026-09確認）",
            "set_villa": {"capacity": "7"},
            "set_spec": {
                         "capacity": {"v": 7, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/tensyukau"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/tensyukau"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/tensyukau"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/tensyukau"}}},

    "218": {"name": "マイグレ600",
            "reason": "公式「露天風呂（伊東天然温泉）・水風呂・オーバーヘッドシャワー・内風呂(伊東天然温泉)」→coldbath=bath（水風呂は2つの天然温泉風呂と別立て）、「定員 5名」「客室は心落ち着く和の茶の間とベッドルームの2部屋。最大5名様ご宿泊可能です。」→capacity=5（**上部表示と本文が一致している**）。**新規に sauna_type=indoor**（部屋一覧に「茶の間、広縁、デッキ、サウナ室、寝室、浴室…」と室内の一室として記載、「室内総檜のサウナ室」）、**loyly=yes**（「オリジナルブレンドの精油アロマでお好きなだけロウリュを。」）、**wifi=yes**。**outdoor_rest は入れない**: 庭のウッドデッキでの体験と書かれているが「外気浴」等の直接語が無い（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"},
                         "capacity": {"v": 5, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/600-sekitei"}}},

    "228": {"name": "マイグレパノラマ",
            "reason": "出典なし6項目すべて一致した。公式「1F： 寝室①、寝室②、浴室、洗面室、トイレ、デッキ、サウナルーム」→sauna_exists / sauna_type=indoor（1Fの室内間取りの一部）、「お風呂 露天風呂・水風呂・内風呂・オーバーヘッドシャワー」「サウナの後は屋外のオーバーヘッドシャワーで汗を流し、2基の浴槽で冷水浴を。」→coldbath=bath、「定員 12名」→capacity、「Wi-Fi 完備」→wifi。**stove は今回も確定できない**（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/panorama"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/panorama"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/panorama"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/panorama"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/panorama"}}},

    "235": {"name": "COCO VILLA 大室山",
            "reason": "出典なし4項目すべて一致した。COCO VILLA は構造化されたスペック表を持っており判定しやすい。「本施設では、電気式サウナを導入しています。」＋設備一覧「サウナ ◯」→sauna_exists、スペック表「セルフロウリュ ◯」→loyly、ハウスルール「水風呂の利用について 水風呂をご用意しています。利用した後は、チェックアウトまでに必ず水を抜くようにお願いします。」→coldbath=bath、スペック表「外気浴 ◯」「ととのい用チェア ◯」＋設備欄「Coleman インフィニティチェア（2台）」→outdoor_rest（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"}}},

    "236": {"name": "Tiny Base The MOUNTAiN",
            "reason": "**coldbath を bath から tub に訂正する。** 公式の MOUNTAiN 共通設備欄に「アウトドアバス（水風呂・お湯張り可能)」とあり、**同じ浴槽を水風呂にもお湯張りにも使える兼用仕様**。名詞が「アウトドアバス」で括弧内が用途なので、tub（浴槽・ジャグジー兼用）の定義に合致する。stove=wood も裏付けが取れた: 「フィンランド式の薪サウナも完備」「フィンランド式の薪サウナは、2段L字構造。」＋共通設備欄「サウナ フィンランド式サウナ(薪) / 薪 /」で**サウナ自体を修飾**している。capacity=4 も SUGI「人数 2～4名」・Hiiragi「人数 2～4名」の両棟一致。**新規に outdoor_rest=yes**（共通設備欄「ととのいスペース」＋「自然の中でマイナスイオンをたくさん浴びる外気浴を存分にお楽しみください。」）。**pet_ok は入れない**: 「愛犬同伴可能」の記述がMOUNTAiN専用かサイト共通か切り分けられなかった（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp/stay/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp/stay/"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp/stay/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp/stay/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://tinybase.co.jp/stay/"}}},

    "261": {"name": "Earthboat Minakami Fujiwara",
            "reason": "出典なし5項目すべて一致した。「サウナ フィンランド式サウナ（薪ストーブ） / 水風呂・温泉露天風呂 / インフィニティチェア」→sauna_exists / outdoor_rest、設備の「柄杓」＋体験欄「自分で薪をくべて温めるフィンランド式サウナ」→loyly、「定員 3名」→capacity、「ペットの受け入れ 可（種類・大きさ・頭数の制限なし）」→pet_ok（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"},
                         "capacity": {"v": 3, "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"}}},

    "262": {"name": "Earthboat Minakami Hodaigi",
            "reason": "出典なし5項目すべて一致した（id=261 と同じ書式）。「サウナ フィンランド式サウナ（薪ストーブ） / 水風呂 / インフィニティチェア」→sauna_exists / outdoor_rest、「柄杓」＋「自分で薪をくべて温めるフィンランド式サウナ」→loyly、「定員 3名」→capacity、「ペットの受け入れ 可（種類・大きさ・頭数の制限なし）」→pet_ok。**新規に coldbath=bath**（藤原と違い温泉との併記が無く「水風呂」単独記載）（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"},
                         "capacity": {"v": 3, "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"}}},

    "271": {"name": "Earthboat Saitama Kawajima",
            "reason": "出典なし3項目が一致した。「サウナ 電気式サウナ / 水風呂（温水利用可） / インフィニティチェア」→sauna_exists / outdoor_rest、設備の「柄杓」→loyly、冒頭紹介文「サウナ、水風呂と外気浴スペース…を設けています。」。**coldbath は bath のまま変更しない**: 「水風呂（温水利用可）」を tub への訂正候補として提案されたが、**名詞が「水風呂」で括弧内が付随的な用途**なので専用の水風呂と読む。id=236 は名詞が「アウトドアバス」で用途が括弧内だったため tub にした。**tub は『何であるか』が浴槽の場合に使い、『水風呂に温水も入れられる』は bath のまま。** 同ブランドの id=122 Nasu も「水風呂（一部客室は温水利用可）」で bath としており揃う（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/saitama_kawajima"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/saitama_kawajima"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/saitama_kawajima"}}},
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
