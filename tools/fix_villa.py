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
    "121": {"name": "COCO VILLA 那須高原",
            "reason": "公式のサウナ仕様表が○✕形式で項目ごとに書かれている。「室内サウナ（Harvia社・電気ストーブ）」→sauna_type=indoor / stove=electric、「セルフロウリュ ◯」→loyly=yes、「水風呂／五右衛門風呂」「水風呂収容人数 2名」→coldbath=bath、「キッチン（IHコンロ3口）」、設備一覧「愛犬同伴 ✕」「ドッグラン ✕」→pet_ok=no、「Wi-Fi ◯」。既存の outdoor_rest=yes も「外気浴 ◯」「ととのいスペース ◯」で裏付けが取れた（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/nasu-kogen/"}}},

    "123": {"name": "RIVER VIEW HOUSE",
            "reason": "公式サイトが存在しない施設。**stove=wood（2026-07・出典なし）は誤り。electric が正しい。** サウナイキタイの構造化データは「ドライサウナ 対流式（ストーン） 電気」と明記している。一休の本文にある「土間リビングに一歩入ると、薪ストーブの炎が迎える」は**リビングの暖房用薪ストーブ**であって、サウナの熱源ではない。あわせてセルフロウリュ「有り」／オートロウリュ「無し」→loyly=yes、「水風呂／温度13度／収容人数2人／水深60~80cm」→coldbath=bath、Wi-Fi「○」。pet_ok は一休 00052428 の「ペット：不可」＋設備欄「× ペット可」で一致。既存の outdoor_rest=yes と capacity=8 も裏付けが取れた（一休「定員 1名～8名」は9名上限より低いので機械的読み取りの疑いは薄い）（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106224"}}},

    "127": {"name": "VillaEL5",
            "reason": "じゃらん「サービス&レジャー：…ペットOK（有料）(ケージ有り/ケージ持込)」「補足：ペットルームあり（完全予約制）…小型、中型犬（大型犬は要相談）」で既存の pet_ok=yes に裏付けが取れた。**feature「6LDK 185㎡」と desc「7LDK 200㎡」の食い違いは決着しなかった。** 4ソースを確認したが割れている: Booking.com本文「広さは、約１８５平米、２階建７LDKとなっており」／Booking.comの部屋タイプ名「6ベッドルーム ハウス」／楽天「6LDK 約200平米」／Agodaのタイトル「7ベッドルーム／190m²」。**運営会社自身がサイトごとに違う数字を出しており**、Booking.com内部でも本文と部屋タイプ名が矛盾している。サウナは「その他の風呂施設：展望風呂（条件有り）・サウナ（有料）・ジャグジー（条件有り）」とあり有料オプションであることは分かるが形式・熱源は不明（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.jalan.net/yad355155/"}}},

    "133": {"name": "GEOSPOT MOTOHAKONE B",
            "reason": "B棟・C棟それぞれに個別の予約ページ・一休ID・サウナイキタイIDがあり、棟ごとに確認した。公式の予約エンジンに棟ごと同一文面で「プライベートサウナ 全客室の2階に、プライベートサウナと水風呂、外気浴が楽しめるテラスを設置。」とある→sauna_type=indoor。**stove=electric はB棟のサウナイキタイで直接確認**「ドライサウナ 対流式（ストーン） 電気」。pet_ok は一休 00052339「ペット：不可」＋設備欄「× ペット可」。wifi は Yahoo!トラベル「wi-fiが利用可能です」。**loyly は入れない**: 「madsaunistが手がける、呼吸法と水療法を組み合わせた独自のロウリュ」とあるが、madsaunist は電気式スチームジェネレーターを展開するブランドでオート機構の可能性があり、セルフ／オートを断定できない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/97214"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/97214"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/97214"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/97214"}}},

    "134": {"name": "GEOSPOT MOTOHAKONE C",
            "reason": "C棟。公式の予約エンジンに B棟と同一文面で「全客室の2階に、プライベートサウナと水風呂、外気浴が楽しめるテラスを設置。」→sauna_type=indoor。pet_ok は一休 00052444「ペット：不可」＋設備欄「× ペット可」。wifi は trip.com「無料Wi-Fi（客室内）」。**stove は入れない**: B棟はサウナイキタイで電気と確認できたが、C棟には個別ページが無く公式の同一文面からの類推になるため（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052444/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052444/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052444/"}}},

    "141": {"name": "koti hakone",
            "reason": "公式「ハルビア社製の6kWヒーターを採用」→stove=electric（kW表記は電気式の根拠）、サウナイキタイも「バレルサウナ ストーブはHARVIA製」→sauna_type=barrel、公式「サウナでしっかりと汗をかいた後は、隣接する水風呂でクールダウンが可能です。」→coldbath=bath、「自然に囲まれたデッキで心と体をリセットしてください」→outdoor_rest=yes。wifi は Booking.com「無料Wi-Fi」。既存の capacity=26 も公式「定員 26名まで」と完全一致した。**loyly は入れない**: 公式「熱せられた石に水をかけて蒸気を発生させるロウリュにより」はセルフとも読めるが、サウナイキタイの構造化データはロウリュを「無し」としており食い違う（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"},
                         "capacity": {"v": 26, "src": "desk", "at": "2026-08",
                                        "url": "https://vacation-koti.jp"}}},

    "144": {"name": "シエロ箱根仙石原",
            "reason": "**coldbath を bath から tub に訂正する。** FAQ「水風呂はありますか」への回答は「浴室に浴槽が2つありますので、水風呂としてご利用いただけます。」、温泉FAQは「浴室に2つ浴槽があり1つは温泉、もう1つは水風呂、もしくはお湯を入れることができます。」で、**専用の水風呂ではなく温水にも切り替えられる兼用浴槽**。2026-08 に追加した選択肢 tub（浴槽・ジャグジー兼用）の定義に合致する。あわせて stove=electric はサウナイキタイ「ドライサウナ 電気」、outdoor_rest はサウナイキタイ「●外気浴 デッキチェア: 2席」、kitchen_type は公式VILLAページ「IHコンロ、卓上IHコンロ」、pet_ok はFAQ「ペットの同伴はご遠慮頂いております。」、wifi はFAQ「全室WIFIの利用が可能となっております。」。既存の sauna_exists / loyly / capacity=12 も「セルフロウリュ対応のプライベートサウナ」「最大宿泊人数は大人12名となっております。」で裏付けが取れた。**sauna_type は入れない**: 浴室と同一棟という構成から indoor が推定できるだけで明記が無い（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://cielo-hakone.jp/faq/"}}},

    "145": {"name": "ICHI-VILLA CROSSROAD HAKONE",
            "reason": "サウナイキタイ「ドライサウナ 対流式（ストーン） 電気」→stove=electric、セルフロウリュ欄の補足「ご自身で好きなだけ（※サウナストーブが壊れない範囲でお願いいたします）」→loyly=yes、「●外気浴 イス: 2席」→outdoor_rest=yes。pet_ok は一休 00052438「ペット：不可」＋設備欄「× ペット可」。wifi は公式設備ページ「家電・大型設備：…Wi-Fi…」＋サウナイキタイの2ソース。既存の sauna_type=tent は公式「テラス席のテント型サウナと水風呂で、温冷交代浴をお楽しみいただけます。」／一休「テントサウナ・水風呂・キッチンを備え」／サウナイキタイ「テントサウナ（常設・定期設置）○」の三重で裏付けが取れた。coldbath=bath も「水風呂 温度16度」。capacity=4 は一休「定員 1名～4名」と一致（公式の「最大6名（大人4名＋添い寝のお子様2名）」とは前提が違うだけ）（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/106225"}}},

    "154": {"name": "LULLA",
            "reason": "公式の宿泊プランページのアメニティ一覧「バレルサウナ、水風呂、サウナハット貸出」→coldbath=bath、「お部屋の情報：部屋サイズ165 m2 / ダブルベッド2台 / 禁煙 / 屋上 / WiFi」→wifi=yes。既存の sauna_type=barrel（一休を出典に記録済み）も同記載で重ねて裏付けられた。**stove / loyly / outdoor_rest / kitchen_type は入れない**: 公式サイトが実質2ページ構成で記載が無く、一休にも無い（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.lulla.jp/宿泊プラン"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.lulla.jp/宿泊プラン"}}},

    "155": {"name": "SAJIMA Funny house",
            "reason": "**ブランド内の別施設との誤認を回避した。** 公式（beach.funnyfunny.jp/funnyhouse-sajima/）はトップ・INFORMATION・FAQのいずれにもサウナの記載が無く、押し出されているのはジャグジーのみ。しかもトップのNEWS欄にあるのは**姉妹施設**「CAP MARTIN Funny house にバレルサウナを新設しました。」の告知だった。本施設固有の告知は一休の「施設からのお知らせ」にあった: 「【サウナ設置のご案内】バルコニーにバレルサウナが登場！プライベートな空間で『ととのう』を是非ご体感下さい。サイズ1,800×1,800」→sauna_type=barrel。同ブランドの記事でも「SAJIMA Funny houseにバレルサウナを設置しました。」と個別に確認した。kitchen_type は公式FAQ「キッチン設備は以下の通りです 電磁調理器（2口）、フライパン…」。既存の sauna_exists / capacity=4 / pet_ok=yes / wifi も公式FAQ「定員は4名様までです」「小型犬一頭のみ宿泊可能です。」「全館Wi-Fiをお使いいただけます」で裏付けが取れた（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051411/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051411/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051411/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051411/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051411/"}}},

    "158": {"name": "GIFTHOUSE 三浦 諸磯",
            "reason": "**capacity=8（2026-07・出典なし）は誤り。6 が正しい。** 公式の部屋案内ページを直接取得して「定員：1〜6名」を確認した（フォトギャラリー・予約エンジンでも一致し、予約エンジンは「定員：1〜6名（未就学児はカウントせず ※3名以上については大人料金）」とより詳しい）。同ページの「IHコンロ×2」→kitchen_type=ih。pet_ok=yes も予約エンジン「同伴可能サイズ：小型犬(2頭まで)、中型犬(1頭まで) 愛犬料金：愛犬1頭1泊あたり5,500円」で裏付けが取れた。**sauna_exists=yes は触らないが疑わしい**: 公式サイト全ページ（トップ／Spa & Activity／お部屋／ギャラリー）にサウナの記載が無く、Spa & Activity の中身は焚き火とBBQのみ。2025年7月のグランドオープンを報じたサウナ専門メディアには「海辺には本格的なテントサウナを準備中とのこと」とあり開業時点では未稼働だった。運営会社のPRリリースにも本施設のサウナへの言及が無い（登場するのは系列の別施設 Ocean Sauna Villa 富津竹岡のみ）。ただし不記載は否定の根拠にならないので値は残す（2026-08確認）",
            "set_villa": {"capacity": "6"},
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://miura.gifthouse.jp/miura/room.php"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://miura.gifthouse.jp/miura/room.php"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://miura.gifthouse.jp/miura/room.php"}}},

    "161": {"name": "Oceanfront Villa Hale Kahakai",
            "reason": "公式「施設について」の部屋一覧「主寝室／パウダールーム／エントランスホール／脱衣所／浴室／サウナ室／トイレ／リネン室…」→sauna_type=indoor（建物内の一室として案内されている）。写真キャプション「本格高温サウナ｜メトス製サウナ｜電気式サウナ｜アレクサ」＋ハウスルール「８．サウナ使用後は、電源をお切りください。」→stove=electric。wifi は tripto.jp の施設ページ。既存値も裏付けが取れた: sauna_exists は見出し「オーシャンフロント×METOS製本格高温サウナの一棟貸しヴィラ」、coldbath は写真キャプション「サウナ後の水風呂｜檜浴槽｜プライベートSPA」、capacity=8 はハウスルール「宿泊施設登録宿泊定員：８名（但し、快適な宿泊は大人４～６人までとお考え下さい。）」、pet_ok=yes はハウスルール「プラン選択（9800円）によりペット同伴可となります。…ペットは、ワンちゃんのみ、２匹まで 各１０kgまで」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.oceanfrontvilla-halekahakai.com/施設を見る"}}},

    "167": {"name": "箱根リゾートyamaki",
            "reason": "**stove=wood（2026-07・出典なし）を削除する。リビングの薪ストーブとの混同。** 公式の施設案内を直接取得したところ、「Wood Stove／薪ストーブ」は**バレルサウナとは別の独立した見出し**で、説明は「薪が燃える炎の灯りは1/fゆらぎによる癒し効果があるといわれています。忙しい日常を忘れ心落ち着くひとときをお過ごしください。」と完全に居室の暖房・演出としての描写。一方バレルサウナ自体の説明は「樽型のバレルサウナは、熱効率・強度に優れ、熱を効率的に循環させることができるため」までで**熱源の記載が一切ない**。pet_ok はFAQ「ペット連れでのご宿泊は、ご遠慮いただいております。」、wifi はFAQ「無料Wi-Fiがございます。」。既存の sauna_exists / sauna_type=barrel / capacity=8 は「樽型のバレルサウナ」とFAQ「1名様～8名様までご宿泊可能です。」で裏付けが取れた。**kitchen_type は入れない**: 「3口コンロ / 卓上IH」とあるが3口コンロの種別が書かれておらず、ガスと断定できない（2026-08確認）",
            "remove_spec": ["stove"],
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://hakone-resort-yamaki.com/facilities.php"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hakone-resort-yamaki.com/facilities.php"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://hakone-resort-yamaki.com/facilities.php"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://hakone-resort-yamaki.com/facilities.php"}}},
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
