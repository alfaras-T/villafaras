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
    "14": {"name": "Sea by TORAMII",
            "reason": "capacity=9 は誤り。公式「お1人様から最大10名様までご利用いただけます。」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://toramii.jp/sea-by-toramii/"}}},

    "17": {"name": "the MELLOW HOUSE 館山",
            "reason": "capacity=9 は誤り。公式「最大20名様まで宿泊可能。（大人12名、子供8名）」より 20 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "20"},
            "set_spec": {
                         "capacity": {"v": 20, "src": "desk", "at": "2026-08",
                                        "url": "https://www.mellowhouse.jp/question/"}}},

    "18": {"name": "On the wave 館山",
            "reason": "capacity=6 は誤り。公式「最大10名（大人6名、子供4名）まで可能です。※子供は未就学児まで。小学生以上は大人カウントとなります。」より 10 に訂正。トップページでも同内容を確認。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://otw-tateyama.com/qa/"}}},

    "19": {"name": "GIFTHOUSE 館山 那古海岸",
            "reason": "capacity=6 は誤り。公式「定員：1〜10名」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://nagokaigan.gifthouse.jp/nagokaigan/room.php"}}},

    "21": {"name": "UMInoTERRACE",
            "reason": "capacity=9 は誤り。公式「2名〜最大12名までご利用いただけます。」より 12 に訂正。推奨6名は comfort_cap。隣接別棟と合わせた24名は除外。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://piyo-terrace.com/vacationrentals/uminoterrace-villa/"}}},

    "25": {"name": "THE POOL HOUSE TOKYO BAY",
            "reason": "capacity=8 は誤り。公式「最大12名（シングルベッド×４、セミダブルベッド×４）までの宿泊」より 12 に訂正。姉妹施設KISARAZU(最大8名)と同ページ内で区別を確認。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://thepoolhouse.jp/"}}},

    "27": {"name": "Sumera Resort Minato",
            "reason": "capacity=3 は誤り。公式「大人3名～5名様まで（本館+別館プラン）」より 5 に訂正。本館のみは3名。villa_type=multi と整合。（2026-08確認）",
            "set_villa": {"capacity": "5"},
            "set_spec": {
                         "capacity": {"v": 5, "src": "desk", "at": "2026-08",
                                        "url": "https://sumera.co.jp/minato/"}}},

    "34": {"name": "Retreat Villa Aym",
            "reason": "capacity=9 は誤り。公式「全3棟利用時 最大30名」より 30 に訂正。feature「1日3組限定」desc「最大30名まで対応可能」と一致。1エントリ＝施設全体。（2026-08確認）",
            "set_villa": {"capacity": "30"},
            "set_spec": {
                         "capacity": {"v": 30, "src": "desk", "at": "2026-08",
                                        "url": "https://aym.wyes-resort.com/"}}},

    "36": {"name": "STAR VILLAGE TATEYAMA",
            "reason": "capacity=9 は誤り。公式「最大利用人数は15名です。それ以上の人数での利用を希望する場合は、必ず事前にご相談ください。」より 15 に訂正。spec=9/desk=10 とも誤り。OTA2件も「基本9名（最大15名様まで）」。（2026-08確認）",
            "set_villa": {"capacity": "15"},
            "set_spec": {
                         "capacity": {"v": 15, "src": "desk", "at": "2026-08",
                                        "url": "https://www.star-village.net/plan"}}},

    "37": {"name": "VILLA SENSE kujukuri",
            "reason": "capacity=9 は誤り。公式「4ベッドルーム、最大定員16名」より 16 に訂正。公式サイトに定員の記載がなくOTA複数一致で採用。stove=wood は誤り。「電気ストーブ（HARVIA） 6人用＋前室あり」より electric に訂正。公式はJS描画で取得不可。運営会社WILL合同会社のプレスリリースで確認。（2026-08確認）",
            "set_villa": {"capacity": "16"},
            "set_spec": {
                         "capacity": {"v": 16, "src": "desk", "at": "2026-08",
                                        "url": "https://travel.yahoo.co.jp/00052168/room/"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://prtimes.jp/main/html/rd/p/000000001.000159602.html"}}},

    "40": {"name": "THE BLUE POINT seaside villa",
            "reason": "capacity=9 は誤り。公式「定員12名様まで」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://aonoie.jp/bluepoint/facilities.html"}}},

    "43": {"name": "Montevan RESORT VILLA",
            "reason": "capacity=9 は誤り。公式「【敷地面積270㎡】リビング＋2ベッドルーム（定員 10名様）」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://www.montevan.com/"}}},

    "51": {"name": "九十九里 point59",
            "reason": "capacity=9 は誤り。公式「一棟貸切 [定員6名] ※追加人数の場合(最大4名様まで)定員10名」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://bai-bain.com/property/017_Point59.html"}}},

    "53": {"name": "tokoro hotel Isumi",
            "reason": "capacity=7 は誤り。公式「Capacity／定員 2~7名（お子様を含め8名）」より 8 に訂正。spec=7は基本人数。規約どおり最大宿泊人数の8を採用。（2026-08確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://tokoro-hotel.com/isumi/overview"}}},

    "55": {"name": "SEA-LIFE TSURIGASAKI",
            "reason": "capacity=9 は誤り。公式「大人10名＋子供9名の最大19名様までとなっております」より 19 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "19"},
            "set_spec": {
                         "capacity": {"v": 19, "src": "desk", "at": "2026-08",
                                        "url": "https://sea-life.ne.jp/faq/"}}},

    "58": {"name": "UMIYAMA CHIKURA",
            "reason": "capacity=6 は誤り。公式「宿泊人数 大人6名・子供3名 (12歳以下) ＊お子様含め最大9名様がご宿泊いただけます。」より 9 に訂正。spec=6 は大人のみの数だった。（2026-08確認）",
            "set_villa": {"capacity": "9"},
            "set_spec": {
                         "capacity": {"v": 9, "src": "desk", "at": "2026-08",
                                        "url": "https://umiyama-chikura.com/"}}},

    "62": {"name": "RICKA KATSUURA",
            "reason": "capacity=9 は誤り。公式「定員人数：12名」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://ricka-resort.com/katsuura/"}}},

    "65": {"name": "THE NALU",
            "reason": "capacity=4 は誤り。公式「ご宿泊人数の上限は、大人4名様および添い寝可能な子ども2名様（合計6名様まで）とします。」より 6 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "6"},
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://the-nalu.com/information/"}}},

    "67": {"name": "EKVOLI MARINA VILLA, Isumi Garden",
            "reason": "capacity=9 は誤り。公式「1日一組限定10名まで大人数で宿泊できる一棟貸タイプ」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ekvoli.com/ekvoli-marina-villa"}}},

    "68": {"name": "SURF UP",
            "reason": "capacity=9 は誤り。公式「宿泊人数 最大14名」より 14 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "14"},
            "set_spec": {
                         "capacity": {"v": 14, "src": "desk", "at": "2026-08",
                                        "url": "https://surf-up.co.jp/"}}},

    "72": {"name": "VILLA LAGI",
            "reason": "capacity=6 は誤り。公式「定員2～14名」より 14 に訂正。トップではなくROOMページに記載。Q&Aの「6名まで同料金」は料金区分で上限ではない。（2026-08確認）",
            "set_villa": {"capacity": "14"},
            "set_spec": {
                         "capacity": {"v": 14, "src": "desk", "at": "2026-08",
                                        "url": "https://www.chiba-isumi-privatevilla.com/room/"}}},

    "77": {"name": "enico.Mt.Fuji smile",
            "reason": "capacity=9 は誤り。公式「Entire home 3 bedrooms 1 bathroom Sleeps 10」より 10 に訂正。公式・公式予約とも定員記載なし。OTA2件一致。旧名 Tocoro. Mt.Fuji Kisaragi で住所一致を確認。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://www.expedia.co.jp/Kofu-Hotels-Tocoro-Mt-Fuji-Kisaragi.h42394041.Hotel-Information"}}},

    "83": {"name": "THE TIME FUJI",
            "reason": "sauna_cap=2 は水風呂の収容人数の取り違え。出典note.comの原文は「屋外にはサウナ利用者専用の水風呂タブ（2名用）」で、2名は水風呂の数字。サウナ定員と取り違えていた。「サウナ室 温度 110 度 収容人数： 6 人」より 6 に訂正。（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 6, "src": "desk", "at": "2026-08",
                                         "url": "https://sauna-ikitai.com/saunas/79203"}}},

    "121": {"name": "COCO VILLA 那須高原",
            "reason": "stove=wood は誤り。「方式：電気式サウナ / サウナストーブ：HARVIA（ハルビア）」より electric に訂正。（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://coco-villa.jp/villa/nasu-kogen/"}}},

    "126": {"name": "御宿 憩（OYADO IKOI）",
            "reason": "capacity=12 は誤り。公式「4LDK約130平米 最大10名様」より 10 に訂正。日本語公式は一貫して10。英語版は冒頭10・設備欄15で自己矛盾。じゃらんの12は登録定員の可能性。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://stay-japan.tokyo/ikoi/"}}},

    "131": {"name": "LEVATA",
            "reason": "stove=wood は誤り。「バレルサウナ（電気式サウナストーブ４人まで）」より electric に訂正。（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://levata.jp/"}}},

    "173": {"name": "軽井沢365 フォレストガーデン八風台",
            "reason": "stove=wood は誤り。「TYLO社の電気ストーブを採用した離れのサウナ小屋と、屋外に水風呂も設置。」より electric に訂正。（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://karuizawa365.jp/stay/happudai"}}},

    "192": {"name": "ポーラーハウスカナディアン南軽井沢1",
            "reason": "capacity=9 は誤り。公式「４名様から１９名様まで宿泊できますので」より 19 に訂正。住所「長野県北佐久郡軽井沢町発地336-1」でDB一致。id=268と定員が同じだが犬同伴可否・駐車台数が異なる別施設。（2026-08確認）",
            "set_villa": {"capacity": "19"},
            "set_spec": {
                         "capacity": {"v": 19, "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/カナディアン南軽井沢1"}}},

    "194": {"name": "海野宿一棟貸し宿　上州屋",
            "reason": "capacity=5 は誤り。公式「最大８名様」より 8 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://joshuya-unnojuku.jp/stay"}}},

    "200": {"name": "enukoti（エヌコティ）",
            "reason": "stove=wood は誤り。「ドライサウナ 対流式（ストーン） 電気 TV無」より electric に訂正。公式はHARVIA表記のみで方式不明。サウナイキタイで電気式と確認。住所も一致。（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://sauna-ikitai.com/saunas/79664"}}},

    "204": {"name": "オーシャンビュー南熱海",
            "reason": "capacity=9 は誤り。公式「定員 12名（推奨8名）」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/minamiatami/"}}},

    "260": {"name": "赤城宿 珠蕾山荘 -shurai-",
            "reason": "capacity=6 は誤り。公式「2つの間を繋げて最大12名での利用も可能です」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://akagi-shuku.com/hotels/shurai-sanso/"}}},

    "268": {"name": "ポーラーハウス南軽井沢1",
            "reason": "capacity=15 は誤り。公式「4名様から19名様まで宿泊できます。」より 19 に訂正。詳細ページの住所「群馬県甘楽郡下仁田町西野牧12514-9」でDB一致を確認。同名別棟「南軽井沢1 with DOG」(8名)「南軽井沢3」(11名)とは別。（2026-08確認）",
            "set_villa": {"capacity": "19"},
            "set_spec": {
                         "capacity": {"v": 19, "src": "desk", "at": "2026-08",
                                        "url": "https://www.polar-resort.com/stay/コテージ紹介-軽井沢/ハウス南軽井沢_1"}}},

    "279": {"name": "大谷石の蔵サウナと古民家宿 DAIGO SAUNA",
            "reason": "capacity=14 は誤り。公式「客室は全部で３室ご用意、最大12名が宿泊できます」より 12 に訂正。サイト内に4通りの数値。断定形で2箇所（stay本文・chillnnプラン説明「最大12名で宿泊できるプラン」）に出る12を採用。プラン名「(9〜14名様はこちら)」と予約UI上限14は予約区分、FAQ「大人8名程度」は程度付き。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://daigo-sauna.jp/stay"}}},
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

    # VILLAS のスカラー項目。同じ値を持つ別施設を誤爆しないよう、
    # "id": N を含む施設オブジェクトの範囲内に限定して置換する。
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
            if k not in VILLA_FACTS:
                continue
            label, fmt = VILLA_FACTS[k]
            new = fmt % val
            s2 = re.sub(r'(<span class="fact-label">%s</span>'
                        r'<span class="fact-val">)[^<]*(</span>)' % re.escape(label),
                        lambda m: m.group(1) + new + m.group(2), s, count=1)
            if s2 != s:
                print("    fact「%s」を %s に更新" % (label, new))
                s = s2

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
        if nb != blk:
            s = s.replace(blk, nb, 1)
            if fx.get("remove_spec"):
                print("    spec: %s を削除" % ", ".join(fx["remove_spec"]))
        write(p, s, orig)
    else:
        print("    spec-data.js に該当なし")

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
