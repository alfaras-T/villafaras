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
    "1": {"name": "古民家宿るうふ 清之家",
            "reason": "公式「サウナ室は定員4名、ロウリュでじっくり汗をかくフィンランドサウナ」→loyly=yes（「フィンランドサウナ」はスタイル呼称なので stove には使わない）、「杉香る貸し切りのサウナと水風呂で疲れを癒やし、縁側でくつろぐ。」→outdoor_rest=yes（サウナ→水風呂→縁側の導線として書かれている）。pet_ok=no は一休 00051530 の基本情報「ペット 不可」＋設備欄「× ペット可」。既存値も裏付けが取れた: 「設備:露天風呂、サウナ、水風呂、シャワー」→coldbath=bath、設備一覧「ガスコンロ」→kitchen_type=gas、「総杉造りの屋外サウナ」→sauna_type=hut。**なお公式サイト内で定員が食い違っている**: 「定員：8名」という記載と「2名〜10名様までご利用いただけます。」が併存する。既存の capacity=10 は「範囲は上限を採る」規約に沿う（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/seinoie"}}},

    "6": {"name": "CAP MARTIN Funny house",
            "reason": "**capacity=5（2026-07・出典なし）は誤り。4 が正しい。** 公式FAQを直接取得して「大人最大4名様 基本料金（2名様）より1名様増える毎15,000円（税込） 10歳未満のお子様は2名様まで無料」を確認した。一休の施設からのお知らせとプラン名も「最大4名様」で3箇所一致し、ベッド構成「シングルベッド×2 キングサイズベッド×1」とも整合する。**一休の部屋種別欄は「定員 1名〜5名」と表示されており、これがそのまま初期投入されたとみられる。9名上限問題と同型のパターンが5でも起きていた。** kitchen_type は公式ROOMページ「3口IHクッキングヒーター/電子オーブンレンジ」。既存値も裏付けが取れた: sauna_type=barrel は公式お知らせ（2025/09/01）「CAP MARTIN Funny house にバレルサウナを新設しました。」と一休の「バルコニーにバレルサウナが登場！」、pet_ok=yes は FAQ「小型犬一頭のみ宿泊可能です。オプションよりお申込み下さい。（8,000円/税込）」、wifi=yes は公式「Wi-Fi完備」。**DBの住所「岩井袋261-3」は公式・一休とも「261-5」で末尾が異なる**（2026-08確認）",
            "set_villa": {"capacity": "4"},
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-cap-martin/faq/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-cap-martin/faq/"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-cap-martin/faq/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-cap-martin/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-cap-martin/faq/"}}},

    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "一休の「温泉・お風呂」欄に「サウナ あり」、公式にも「サウナもあるので、冬はサウナ後の水風呂としてプールをご活用ください。」で既存の sauna_exists=yes に出典を付ける。**kitchen_type は入れない**: 一休は「○ キッチンあり」のみでIH/ガスの別が不明（2026-08確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052349/"}}},

    "253": {"name": "伊豆グランピングリゾートIshiki385",
            "reason": "公式「フルフラットチェアやデッキチェア」が整いスポットとして利用可→outdoor_rest=yes、公式 /stay/ の「Free WiFi」→wifi=yes、「グランピングテントは１組様ごとにプライベートゾーンとなっておりますので、ペットと一緒にまるで我が家のようにお寛ぎいただけます。」→pet_ok=yes の裏付け。既存の sauna_type=barrel も公式「本格北欧スタイルの屋外型バレルサウナ」で裏付けられたが、**テントサウナも別に実在する**（DBの紹介文「テントとバレル、2種のサウナ」とも符合）ため代表値としては不完全。**stove は入れない**: サウナイキタイの写真キャプションが「バレルサウナ 電気式セルフロウリュ」「テントサウナ 薪式セルフロウリュ」と2種を別々に書く一方、同ページ上部の構造化データは「対流式（ストーン）／薪」で内部矛盾している。**coldbath も入れない**: 「敷地内の沢での冷水浴も利用できます」（サウナのあるマウンテンサイドエリア）と別エリアの「屋外冷水風呂」が併存し一本化できない。**capacity=6 は要再検討**: 客室別の定員はドームテント2-4名／サファリテント2-6名／ロッジ2-3名でばらついており、6はサファリテントの上限とのみ一致する（2026-08確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://izuglam385.com/features/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://izuglam385.com/features/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://izuglam385.com/features/"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://izuglam385.com/features/"}}},

    "255": {"name": "貸別荘「碧 ai」",
            "reason": "公式「サウナから出た後は専用の水風呂で体をクールダウン。」→coldbath=bath（屋上ジャグジーは「体の芯からポカポカに温まります」と明記され温浴設備なので別物）、「ジャグジーの後は、リクライニングチェアで、日光浴や風を感じながらリラックスできます。」→outdoor_rest=yes。FAQ「大切なご家族と思いますが、当別荘ではペットの受け入れをしておりません。」→pet_ok=no（明示的な否定文）、「ご利用いただけるWi-Fi環境を整備しております。」→wifi=yes。既存値も裏付けが取れた: sauna_type=tent は /about/ の本文「庭でテントサウナ 屋上でジャグジー」（トップは画像altのみだったが本文で確定）、capacity=10 は「1日1組、10名様迄」（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"},
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"},
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ai-inc.net/enjoy/"}}},

    "258": {"name": "ALIVIO LUXE",
            "reason": "公式の間取り欄「檜サウナ／リビング／ダイニング／キッチン／浴場／寝室3部屋」と居室と並んで列挙されている→sauna_type=indoor（「檜」は室材の呼称で熱源ではない）。予約サイト「フィンランドサウナに隣接する『Meditative Bath』は…サウナ後の火照りを静かに鎮め…クールダウン・エクスペリエンスをご提供します。」→coldbath=bath、「開放感あふれる『ザ・ギャラリーデッキ』をプライベートな休憩スペースとして」→outdoor_rest=yes。既存の capacity=8 も公式「最大8名」で裏付け。**stove は入れない**: 「本格フィンランドサウナ」はスタイル名（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://ankr-resort.team/alivio/luxe/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://ankr-resort.team/alivio/luxe/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://ankr-resort.team/alivio/luxe/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://ankr-resort.team/alivio/luxe/"}}},

    "259": {"name": "赤城宿 清芳山荘 -seiho-",
            "reason": "本館の設備「檜風呂、サウナ、水風呂、シャワー」で既存の coldbath=bath に出典を付ける。**sauna_type / stove は代表値を決められないので入れない**: 本館は「檜風呂、サウナ、水風呂、シャワー」とのみ書かれ形式の記載が無く、奥庫・質庫は「プライベートテントサウナもあり、自然の中で思う存分、ととのえます。」でテント。棟によって形式が違う（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://akagi-shuku.com/seiho-sanso/honkan/"}}},

    "263": {"name": "アウトドア貸切別荘北軽井沢1",
            "reason": "公式の「野外サウナ」表記だけでは形式が決まらないため、住所一致を確認したうえでサウナイキタイとAirbnbを追加で確認した。公式の画像キャプション「アウトドア貸切別荘北軽井沢Iのテントサウナ」＋サウナイキタイのアウトドアサウナ欄「テントサウナ（常設・定期設置） ○」→sauna_type=tent。構造化欄の「薪」→stove=wood、「セルフロウリュ: 有り」→loyly=yes、「外気浴: 有り」「休憩スペース: 有り（イス6席）」→outdoor_rest=yes。**サウナイキタイの構造化欄はサウナ室の項目なので、Airbnbの「食材、着火剤、薪や炭だけでOK」（BBQ用と読める）とは別物として扱った。**既存の pet_ok=no も Airbnb のハウスルール「●ペットについて ペット連れでのご利用はご遠慮願います」で独立に裏付けられた。**coldbath は入れない**: 公式・Airbnbに水風呂の記載が無く、ゲストレビューの言及は根拠にしない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/50440"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/50440"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/50440"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/50440"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/50440"}}},

    "265": {"name": "アウトドアアトラクション北軽井沢",
            "reason": "サウナイキタイのアウトドアサウナ欄「テントサウナ（常設・定期設置） ○」＋補足情報「庭に常設してあるテントサウナを滞在中自由に利用いただけます」→sauna_type=tent。**他の項目は入れない**: 同ページはサウナ室自体の構造化データが未入力（温度・熱源とも不明）で、公式にも記載が無い。id=263 の値は流用しない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/88532"}}},

    "266": {"name": "温泉グランピングシマブルー",
            "reason": "公式サウナページ「フロアには露天風呂タイプの水風呂もご用意。」→coldbath=bath。FAQ「Q: ペットは泊まれますか？」→「ご宿泊はお断りしております。」→pet_ok=no、「コテージ、シマブルーフロント&カフェ共にwi-fiが繋がっております。」→wifi=yes。既存の loyly=yes も公式の「セルフロウリュウ」表記と一致。**sauna_type は入れない**: 「コテージの間に設けられた専用の入口から階段を降りた場所に佇む『森のサウナ』」から独立構造物とは読めるが「小屋」の明示が無い。**kitchen_type も入れない**: FAQ「BBQ機材はお部屋により『ガス式』または『炭式』」はBBQコンロの話で居室のキッチンではない。**capacity=4 は要再検討**: 7棟の定員は2〜6名でばらついており、4はブラウンプレミアムの上限とのみ一致する（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://shimablue.jp/faq/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://shimablue.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://shimablue.jp/faq/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://shimablue.jp/faq/"}}},

    "274": {"name": "サンライズヴィラ大洗",
            "reason": "**pet_ok=yes（2026-07・出典なし）は誤り。no が正しい。** 一休 00051702 を直接開いて住所「〒311-1311 茨城県東茨城郡大洗町大貫町256-327」の一致を確認したうえ、設備欄「× ペット可」と基本情報の全文を確認した。「動物の種類・大きさを問わず、ペット連れでのご宿泊、館内のご利用はご遠慮いただいております。ただし、盲導犬、介助犬は、館内では規制はございませんのでご同伴いただけます。」index.html のペットタグも削除する。同ページ「天然水のこだわりの水風呂を完備しております。」→coldbath=bath（ガーデンプールは「ヒートポンプによる加温方式」で温水なので別物）。wifi は公式FAQ「全室Wi-Fiを完備しております。」。**sauna_type / outdoor_rest は入れない**: サウナイキタイの投稿由来の情報しかない。なおレビューの「暖炉の火に癒された」はバーラウンジの焚き火で、サウナの熱源とは無関係（2026-08確認）",
            "remove_tags": ["pet"],
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051702/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051702/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051702/"}}},

    "275": {"name": "ときわ邸 M-GARDEN",
            "reason": "**kitchen_type=none をこの項目で初めて記録する。** 一休の設備・特徴欄に「× キッチンあり」と○✕形式で明示されており、共通アメニティも冷蔵庫・電子レンジ等のみでキッチン設備が無い。CLAUDE.md が「kitchen_type は否定値を一度も記録していない」と書いていた項目。coldbath=tub は「お部屋にはサウナと屋外ジャグジーも完備」「屋外ジャグジー＆サウナ付き」「ロウリュサウナ＆ジャグジー付き」と複数箇所でサウナとジャグジーが対で書かれ、別途「水風呂」の記載が一切ないため。sauna_type=indoor は「お部屋にはサウナ…を完備」と居室内設備として書かれ、屋外ジャグジーとは対比的にサウナに「屋外」の形容が無い点から。既存の sauna_exists=yes と capacity=6 も「最大6名: 主賓室2名+和室1・2名+和室2・2名」で裏付け。**DBの住所「常磐町1-2-43」は公式・一休とも「1-2-45」で末尾が異なる**（2026-08確認）",
            "set_spec": {
                         "kitchen_type": {"v": "none", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051459/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051459/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051459/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051459/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051459/"}}},

    "284": {"name": "ALOHA GLAMPING RESORT SAKAI",
            "reason": "住所一致を確認したうえでサウナイキタイの構造化欄「サウナ小屋（屋外・水着着用） ○」→sauna_type=hut、「ドライサウナ／対流式（ストーン）／電気」→stove=electric、「五右衛門風呂のような風呂釜に水道水」→coldbath=bath、設備欄「Wi-Fi ○」。kitchen_type は公式 /room/ の「コテージには『IHコンロ（3口）』が設置されています。」。既存の capacity=6 も公式「2名〜4名（最大6名）」が全コテージ共通で裏付けられた（id=253/266 と対照的に棟間で差が無い）。**pet_ok は入れない**: 公式 /dog/ に「全4棟のコテージのうち、2棟は愛犬と泊まれるように」とあり、4棟中2棟のみ可で単一値にできない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/81024"}}},
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
