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
            "reason": "公式ROOMページ TERRACE設備・備品「デイベッド×2/BBQスペース/テーブルセット/流し台/ジャグジー/シャワーブース/バレルサウナ」→sauna_type=barrel、KITCHIN欄「…／３口IHキッチン／…」＋FAQ「キッチンの設備について教えてください」→「電磁調理器（3口）、フライパン…」の2箇所で kitchen_type=ih。**outdoor_rest は入れない**: デイベッドはバレルサウナと同じTERRACE設備一覧に並ぶが、サウナ後の休憩と明示的に結びつける文が無い。**coldbath も入れない**: ジャグジーとシャワーブースの両方があるがどちらを水風呂代わりにするかの記載が無い。公式NEWSにある同ブランド「CAP MARTIN Funny house」のバレルサウナ新設のお知らせとは混同していない（2026-08確認）",
            "set_villa": {"ikyu": "https://www.ikyu.com/00051601/"},
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/andsun-hungfive/room/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/andsun-hungfive/room/"}}},

    "35": {"name": "by the river Isumi",
            "reason": "一休の設備・特徴「× ペット可」＋基本情報「ペット 不可」で両欄一致。FAQ「ネット接続は可能ですか？」→「接続可能です。・wi-fiが利用可能です。」。**他4項目は入れない**: 公式はWixのJSレンダリングでSPEC欄が取得できず、公式予約chillnnの設備ラベルも「専用キッチン」「客室サウナ」までで区分が無い。「バスタブ」はバスルームアメニティ枠内の通常浴槽とみられ水風呂と断定できない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051694/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051694/"}}},

    "48": {"name": "庄屋の里 古民家たなか",
            "reason": "住所「千葉県いすみ市岬町椎木1589」の一致と、施設タイプが「一棟貸し」でタブが1つのみ（男女別が無い）ことを確認して採用。スペック欄「ドライサウナ 対流式（ストーン） 薪」＋ノート「自分で薪を焚べるスタイルになります｜薪ストーブが2基備わっている」→stove=wood、セルフロウリュ＝有り／オートロウリュ＝無し→loyly=yes、外気浴＝有り「●外気浴 デッキチェア: 2席」→outdoor_rest=yes。**coldbath=pool**: ノート「長さ8mｘ幅4mのプールが水風呂代わりです」は**プールを冷却に使うことの明言**で、2026-08 に追加した選択肢 pool の定義に合致する。公式は「プール横に設置されたサウナ」とは書くが水風呂の語が無い。wifi は一休FAQ（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/12959"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/12959"},
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/12959"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/12959"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/12959"}}},

    "51": {"name": "九十九里 point59",
            "reason": "公式「2階お風呂にはサウナとシャワー室も完備しております。」＋施設概要「2階…お風呂・パウダールーム…サウナ・シャワー室」→浴室内の設備なので sauna_type=indoor（代理店 aco.co.jp も独立に「2Fバスルームにサウナ完備」）。wifi は一休FAQ。**loyly は入れない**: 代理店2社が「ロウリュウも楽しめます」で一致するが公式ではなく、セルフ／オートの区別も無い。**WebSearchの要約が「MOKI社製薪ストーブ」「サウナ小屋8名収容」「プールが水風呂代わり」という具体的な記述を出したが、引用元とされたページを直接取得しても該当記述が無く、一休の設備欄は「× プールあり」でプール自体が存在しない。別施設の情報が混入した誤要約だった**（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://bai-bain.com/property/017_Point59.html"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://bai-bain.com/property/017_Point59.html"}}},

    "67": {"name": "EKVOLI MARINA VILLA, Isumi Garden",
            "reason": "住所「千葉県いすみ市岬町江場土2232-1」と名称の一致を確認。「ドライサウナ 対流式（ストーン） 薪」→stove=wood、「水風呂 温度15度 収容人数6人」と独立項目で明記→coldbath=bath、外気浴＝有り・休憩スペース＝有り→outdoor_rest=yes。**loyly=yes は男女共用タブの値を採った**（男湯/女湯タブでは無しだが、1日1組貸切という施設の実態に合うのは男女共用タブ）。wifi は一休FAQとサウナイキタイ設備欄の2ソース（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/86648"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/86648"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/86648"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/86648"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/86648"}}},

    "95": {"name": "天空の温泉ヴィラ紬 河口湖",
            "reason": "一休FAQ「wi-fiが利用可能です」＋公式の設備アイコン「Wi-Fi」。**サウナ関連は入れない**: サウナイキタイに完全一致の施設ページがあるが構造化スペック欄が全て未記入で、詳細は宿泊者の投稿にしか無い（レビューの情景描写は根拠にしない）。さらに投稿から「丘の斜面に全部で5棟あり、上部はバルコニー付きヴィラタイプ、下部は焚き火可能なグランピングタイプ」と分かり、id=95 がどちらの棟を指すか特定できない（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051940/"}}},

    "99": {"name": "ハンズアウトドアリゾート",
            "reason": "公式FAQ「薪割体験やテントサウナなどのご用意がございます。」＋予約サイト glampicks「【テントサウナ】VILLAのお部屋のみとなります。」→sauna_type=tent。後者は既存の sauna_exists=room とも整合する。**kitchen_type は入れない**: 一休の設備欄は「× キッチンあり」だが、VILLA／PAO／OUTDOOR RESIDENCE の3客室タイプがありどの代表室を指すか不明。**stove も入れない**: 「薪割体験」はテントサウナと並列表記されているだけで熱源の記述ではない。なお2023年5月新設の「露天サウナ樽」（時間制・6名まで・有料予約制）は VILLA室内のテントサウナとは別の共用寄り設備なので混同しない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://hanz-odr.com/hanz-faqs/"}}},

    "107": {"name": "ReTune | SPA & SAUNA / VILLA",
            "reason": "公式FAQ「チェックイン時にお渡しする薪で、およそ１時間程度お楽しみいただけます。」「サウナ1回分の薪とロウリュ用のグッズ、バスタオルはご用意しております。」→stove=wood / loyly=yes、公式トップ「外気浴でインフィニティチェアに寝転んで」＋FAQ「デッキには４脚ご用意がございます」→outdoor_rest=yes、PR TIMES「主な設備:テントサウナ、水風呂（天然地下水）、露天風呂」「テントサウナ後に天然地下水の水風呂へ入り」→coldbath=bath、FAQ「WiFiは利用できますか？」→「無料でご利用いただけます。」。公式FAQ・公式トップ・プレスリリースが相互に一致した（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://retune.jp/retune_faq"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://retune.jp/retune_faq"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://retune.jp/retune_faq"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://retune.jp/retune_faq"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://retune.jp/retune_faq"}}},

    "112": {"name": "private villa ietona",
            "reason": "公式「浴槽／シャワー／サウナ／水風呂」と独立項目で明記→coldbath=bath、「シンク／IH／冷凍・冷蔵庫」→kitchen_type=ih。一休「サウナ：ビルトインフィンランド式サウナ、ロウリュ、水風呂、外気浴を備えています」の**ビルトイン**から sauna_type=indoor。wifi も一休。**stove は入れない**: 「フィンランド式」はスタイルの呼称で熱源ではない。**loyly も入れない**: ロウリュの存在は明記されるがセルフ／オートの区別が無く、loyly は3択なので決められない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://ietona.com/about"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://ietona.com/about"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://ietona.com/about"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://ietona.com/about"}}},

    "119": {"name": "SANU 2nd Home 那須2nd",
            "reason": "公式マガジン「SANU CABIN BEE with Sauna」が対象拠点として「八ヶ岳2nd／那須1st／**那須2nd**／北軽井沢2nd／八ヶ岳3rd／白馬1st／河口湖2nd／南アルプス1st／館山1st」と名指ししているため一律適用ではない。「SANU CABIN BEEに設置しているのは、『ONE SAUNA』のバレルサウナ。」→sauna_type=barrel、「テラスに水風呂とととのい椅子を備えています。」→coldbath=bath、「オープンエアの外気浴で心地よいひと時をお過ごしください。」→outdoor_rest=yes、「ロウリュ用バケツ／柄杓」の常備→loyly=yes（W4-3でMOSS型に同じ根拠で採用済み）。wifi は一休。**stove は入れない**: 記事に電気／薪／ヒーターいずれの語も無く、ONE SAUNA社は電気・薪の両モデルを扱っている（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-bee"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-bee"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-bee"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-bee"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-bee"}}},

    "120": {"name": "SANU 2nd Home 那須3rd",
            "reason": "**那須3rd は BEE型ではなく SANU STUDIO RAY 型**（sa-nu.com/list/rayl_nasu3rd）と判明したため id=119 のBEE型記事は流用していない。RAY型を名指しする別記事「SANU STUDIO RAY with Onsen」から「外気浴が心地よいテラス」→outdoor_rest=yes、「ロウリュ用バケツ／柄杓、風呂桶、屋外サンダル×2足をご用意しています」→loyly=yes。wifi は一休FAQ。**sauna_type / stove は入れない**: RAY型には「ONE SAUNAのバレルサウナ」のような明記が無い。**coldbath も入れない**: 記事本文に「水風呂」の語が一度も出ず、天然温泉の露天風呂＋サウナ＋外気浴の構成のみ。沈黙は none の根拠にならない（2026-08確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/onsen"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/onsen"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/onsen"}}},

    "231": {"name": "Hiire IZU FUTO",
            "reason": "公式予約サイトの注意事項「特に、水着未着用での屋外の水風呂や整いスペースのご使用は固く禁じられております。」→coldbath=bath / outdoor_rest=yes（禁止事項の文が設備の存在を前提としている）。pet_ok は一休の設備欄「ペット可：✕」＋基本情報「ペット：不可」で一致。**sauna_type / stove / loyly / kitchen_type は入れない**: hi-ire.com の「しつらえ」欄は OLIVE/OMURO/FUTO の3棟共通の記載で棟別の区別が無く、「サウナ」「専用キッチン」としか書かれていない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-futo.snack.chillnn.com/ja/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-futo.snack.chillnn.com/ja/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-futo.snack.chillnn.com/ja/"}}},

    "233": {"name": "Hiire IZU OMURO",
            "reason": "id=231 と同一ブランドだが棟ごとに個別URLがある公式予約サイトで確認した。「水着未着用での屋外の水風呂や整いスペースのご使用は固く禁じられております」→coldbath=bath / outdoor_rest=yes。pet_ok は一休の設備欄「ペット可：✕」＋基本情報「ペット：不可」で一致（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-omuro.snack.chillnn.com/ja/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-omuro.snack.chillnn.com/ja/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-omuro.snack.chillnn.com/ja/"}}},

    "238": {"name": "月と太陽",
            "reason": "一休「Wi-Fi：○」＋公式「備品 Wi-Fi」。**サウナ関連と coldbath は入れない**: 公式は同一敷地に EN ATAMI / BASE ATAMI / HANABI / DREAM VILLA の4棟を展開しており、**DBの紹介文自体が「4タイプの貸別荘をご用意。全ての施設で、温泉・サウナ・バーベキューをお楽しみいただけます。」と書いているのでこのエントリはブランド単位**。定員5が DREAM VILLA と一致するものの、同棟のページから拾った loyly=yes / coldbath=tub / stove=electric / outdoor_rest=yes をブランド単位のエントリに入れると棟の取り違えになる（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051474/"}}},

    "248": {"name": "エンゼルフォレスト中伊豆",
            "reason": "公式の4名タイプページ「設備・備品 Wi-Fi、家具・電化製品…」。**サウナ関連は入れない**: 公式の客室は4名タイプ（54.65㎡）と6名タイプ（107.72㎡・サウナ付きデラックス）の2種類で、**サウナがあるのは6名タイプだけ**（お知らせ「サウナ付き107.72㎡のデラックスタイプ」2024.6.10）。DBの capacity=4 はサウナなしの4名タイプと一致する。6名タイプの仕様を流用するとブランド内流用の誤りになる。既存の sauna_exists=room はこの構造と整合している（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.angel-hotels.com/angelforest-rental-villa/nakaizu/stay/type4/"}}},

    "260": {"name": "赤城宿 珠蕾山荘 -shurai-",
            "reason": "一休の設備欄「ペット可：✕」＋基本情報「ペット：不可」で一致、「Wi-Fi：利用可能」（公式の設備一覧には Wi-Fi の記載が無い）。**サウナ関連は入れない**: 華の間・蕾の間とも「お風呂 設備：石風呂、サウナ、シャワー」「プライベートサウナ」としか書かれていない。なお公式サイト内で定員が食い違っており、華の間ページは「蕾の間を併用することで12名まで」、蕾の間ページは同じ組み合わせを「14名様まで」と書いている。DBの12は前者と一致（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051890/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051890/"}}},

    "263": {"name": "アウトドア貸切別荘北軽井沢1",
            "reason": "公式の家電製品欄「…エアコン／無線LAN」。**sauna_type は入れない**: ガーデン設備は「野外サウナ」とのみ記載でテント／バレル／小屋の区別が無い。姉妹棟IIの「テントサウナ」を流用しない（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://kashikiribesso.com/outdoor-cottage-kitakaruizawa-1/"}}},

    "264": {"name": "アウトドア貸切別荘北軽井沢2",
            "reason": "公式のガーデン設備「バーベキュー焚火台／テントサウナ／ピザ窯…」→sauna_type=tent、家電製品「…エアコン／ストーブ／無線LAN」→wifi。**stove は入れない**: 家電製品欄の「ストーブ」はTV・洗濯機・冷蔵庫と並ぶ居室の暖房器具であり、サウナのストーブではない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://kashikiribesso.com/outdoor-cottage-kitakaruizawa-2/"}}},

    "265": {"name": "アウトドアアトラクション北軽井沢",
            "reason": "公式の家電製品欄「…ストーブ／無線LAN」。**sauna_type は入れない**: 「野外サウナ」のみでII棟の「テントサウナ」を流用しない。**stove も入れない**: 家電製品欄の「ストーブ」は居室の暖房器具（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://kashikiribesso.com/outdoor-attraction-kitakaruizawa/"}}},

    "268": {"name": "ポーラーハウス南軽井沢1",
            "reason": "**酷似名の別施設との取り違えを住所で回避した。** 検索で最初に出るURL（末尾に _1 が無いもの）は長野県軽井沢町の「南軽井沢3」で、正しいのは末尾 _1 のページ。住所「群馬県甘楽郡下仁田町西野牧12514-9 和美別荘4-14」がDBと一致する。「1階サウナ室…本格3人用ナチュラルサウナ」→sauna_type=indoor（id=192 ポーラーハウスカナディアン南軽井沢1 と同じ書式・同じ判断）。**stove は入れない**: 「薪ストーブ（使用期間 12月～3月）」は「床暖房（使用期間 12月～3月）」と並記されており居室の暖房用。ポーラーの「ナチュラルサウナ」は同ブランドのブログで遠赤外線と自己分類されており、いずれにせよ wood ではない。定員は「定員:16人迄（3人迄追加・最大19人迄）」で既存の19と一致（id=192 の19とは基数が違い偶然の一致）（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/ハウス南軽井沢_1"}}},

    "281": {"name": "SPA＆ごはんゆるうむ",
            "reason": "FAQ Q11「Free wi-fiがございます。」。**サウナ関連は入れない**: 公式「全10棟（サウナ付き 3棟・岩盤浴付き 6棟）」「定員：4名様まで」で、DBの capacity=4 は全棟共通のためどの棟か特定できない。既存の sauna_exists=room はこの構造と整合している。FAQ Q21「宿泊棟には何がついていますか？」の回答にキッチン・ペット・水風呂の記載が無いが、**これは「ある物だけを列挙する」形式なので否定の根拠にならない**（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://yuluumu.co.jp/stay/"}}},

    "283": {"name": "THE BOTANICAL RESORT 林音（リンネ）",
            "reason": "「地下から組み上げた井戸水を使用した水風呂で、火照った体を一気にクールダウン」→coldbath=bath、ガーデンサウナのページ「複数の「ととのい椅子」が用意されている屋外リラックスゾーンが完備」→outdoor_rest=yes。**sauna_type は入れない**: 「ガーデンサウナ」という名称と「収容人数30人の大型のサウナ室」が両立し、屋外の独立構造物か建物内の大部屋か判断できない。**stove も入れない**: 「フィンランドのHARVIA社製のサウナストーブ」とあるがHARVIA社は薪式・電気式の両方を製造している。**loyly も入れない**: 「ロウリュサウナ」「アウフグースイベント」とあるがセルフ／オートの区別が無い。既存の sauna_exists=shared は「男女共用・日帰りOK」の明示と整合している（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://rinne-resort.jp/rinnenoyu/ofuro"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://rinne-resort.jp/rinnenoyu/ofuro"}}},
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
