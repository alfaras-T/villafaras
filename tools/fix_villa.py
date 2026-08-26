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
    "88": {"name": "hotel norm. fuji",
            "reason": "「富士山麓の湧水」→water_src=spring、「愛犬とのご宿泊を、無償で受け付けております」、「ハンモックやリクライニングチェア」→outdoor_rest=yes / rest_chair=chair。姉妹施設 air（長浜2021）・ao（長浜2108）と住所もドメインも酷似するため、/dogs ページで住所「長浜2109-1」を確認したうえで採用した（2026-08確認）",
            "set_spec": {
                         "water_src": {"v": "spring", "src": "desk", "at": "2026-08",
                                         "url": "https://www.hotel-norm.com/dogs"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://www.hotel-norm.com/dogs"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.hotel-norm.com/dogs"},
                         "rest_chair": {"v": "chair", "src": "desk", "at": "2026-08",
                                          "url": "https://www.hotel-norm.com/dogs"}}},

    "93": {"name": "ヴィラグリファーム七里岩",
            "reason": "「バレルサウナ」「薪ストーブのサウナ」「不可」（ペット）。サウナ温度は「最高温度が140℃に達した」とあるが、140℃は validate.py の許容範囲（40〜130℃）を超えるうえ体験談的な表現のため入れない。capacity も「VILLA山と空」単棟6名と2棟合計11名があり代表値を決められないため変更しない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://greefarm.jp/facility-introduction/"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                     "url": "https://greefarm.jp/facility-introduction/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://greefarm.jp/facility-introduction/"}}},

    "94": {"name": "abrAsus hotel Fuji",
            "reason": "**capacity=6 は誤り。** 公式FAQに「少々狭くなりますが、8人まで泊まることができます」とあり8が正しい。あわせて「フィンランドから直輸入の、薪をくべる本格サウナ」→stove=wood、FAQ「Q:ロウリュは、できますか？ A:ご利用いただけます。」→loyly=yes、「富士山の見える、水風呂がございます」→coldbath=bath、FAQ「夏場は、20度前後。それ以外の季節は、15度以下となります」→**water_temp は「夏場の水温」の定義と設問が完全に一致し t1822**、ペット可（2026-08確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://abrasushotel.jp/fuji/faq/"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                     "url": "https://abrasushotel.jp/fuji/faq/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://abrasushotel.jp/fuji/faq/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://abrasushotel.jp/fuji/faq/"},
                         "water_temp": {"v": "t1822", "src": "desk", "at": "2026-08",
                                          "url": "https://abrasushotel.jp/fuji/faq/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://abrasushotel.jp/fuji/faq/"}}},

    "99": {"name": "ハンズアウトドアリゾート",
            "reason": "FAQ「ヴィラS1・S2に限り、2名様で愛犬（11kgまで）同伴宿泊可能」「無料でご利用頂けます」（Wi-Fi）。sauna_type はトップ・FAQが「テントサウナ」、別棟 Outdoor Residence が「露天サウナ『樽』」と棟により異なるため入れない。kitchen_type もゲストハウス棟のみの確認なので入れない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://hanz-odr.com/hanz-faqs/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://hanz-odr.com/hanz-faqs/"}}},

    "100": {"name": "MT.FUJI SKY CABIN",
            "reason": "「サウナ水風呂」→coldbath=bath、「ウッドデッキ」「外気浴スペース」、「IHグリル」、「愛犬※も、一緒にお泊り頂けます」（小型犬のみ）。capacity は公式が「4つのベッド」「1組限定」のみで人数の明記がなく、一休の「定員1名〜6名」はOTA上限表記のため採らない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://mtfuji-camp-resort.jp/mtfujiskycabin/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://mtfuji-camp-resort.jp/mtfujiskycabin/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://mtfuji-camp-resort.jp/mtfujiskycabin/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://mtfuji-camp-resort.jp/mtfujiskycabin/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://mtfuji-camp-resort.jp/mtfujiskycabin/"}}},

    "103": {"name": "Private villa FujiNagi",
            "reason": "「バレルサウナ、水風呂付き」→sauna_type=barrel、FAQ「申し訳ございません。ご宿泊いただくことができません。」（ペット）、「IHコンロ」、「インフィニティチェア」→rest_chair=infinity / outdoor_rest=yes、「チェックイン〜23時まで、翌朝6時〜10時まで。連泊中は朝6時〜23時まで」→sauna_hours=limited（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://www.fujinagi.com/overview-facility.html"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.fujinagi.com/overview-facility.html"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://www.fujinagi.com/overview-facility.html"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://www.fujinagi.com/overview-facility.html"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.fujinagi.com/overview-facility.html"},
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://www.fujinagi.com/overview-facility.html"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.fujinagi.com/overview-facility.html"}}},

    "108": {"name": "THE THIRD PLACE Mt.Fuji",
            "reason": "設備欄に Wi-Fi の記載。棟別定員は 煌Köu 4名／燈Töu 6名／燿Yöu 6名 で、既存の capacity=6 は燈・燿と一致する。サウナがあるのは煌のみ（sauna_exists=room で確定済み）だが、DBの1エントリがどの棟を指すか特定できないため capacity は変更しない（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.chillnn.com/ja/19ad918d44dad/"}}},

    "114": {"name": "エンゼルフォレスト那須",
            "reason": "「ワンちゃんの同伴 3頭まで」、Wi-Fi あり。**sauna_exists は room のまま変更しない。** 共用の天然温泉「白鷺の湯」にサウナがあり日帰り客も利用できる（shared 相当）一方、ルンド・ルオント・グランノッカ・ノッカは「サウナつき」でフィーカ・1541 は記載がない（room 相当）という併存構造で、単一値に決められない。なおルオント公式の「冬季期間は、お部屋の薪ストーブをお楽しみいただけます」は**客室の暖房用**であってサウナの熱源ではないため stove には採らない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ang-ns.com/stay/luonto/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.ang-ns.com/stay/luonto/"}}},

    "127": {"name": "VillaEL5",
            "reason": "公式サイトが失効しておりじゃらんが登録URL。「5名まで宿泊可能」「全館LAN」。ペットは「相談可」で無条件の可ではないため pet_ok は入れない。調査中に「Rakuten STAY VILLA 日光」（薪ストーブ65〜95℃・水風呂・外気浴デッキ）が出たが、住所が所野1550-6 でこの施設の今市1078-4 と一致しないため不採用とした（2026-08確認）",
            "set_villa": {"capacity": "5"},
            "set_spec": {
                         "capacity": {"v": 5, "src": "desk", "at": "2026-08",
                                        "url": "https://www.jalan.net/yad355155/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.jalan.net/yad355155/"}}},

    "128": {"name": "Haga Farm＆Glamping（芳賀ファーム&グランピング）",
            "reason": "「国産総ヒノキ造り『森のバレルサウナ』」→sauna_type=barrel、「貸切（各45分）14：30～、15：30～、16：30～ フリータイム17：30～20：30、翌朝7：00～10：00」→sauna_hours=reserve、「牧場内のサラブレッドへの影響がある為ペットの同伴ではご利用頂けません」、「全室Wi－Fi」。kitchen_type は「アウトドアキッチン（ウェーバー社製ガスグリル）」でBBQ用のため入れない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://hagafarm.com/experience/"},
                         "sauna_hours": {"v": "reserve", "src": "desk", "at": "2026-08",
                                           "url": "https://hagafarm.com/experience/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://hagafarm.com/experience/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://hagafarm.com/experience/"}}},

    "136": {"name": "ASNOVA RESORT NOIE HAKONE SENGOKUHARA",
            "reason": "OKU SUITE・SHIRO SUITE 共通で「セルフロウリュもできる本格的なフィンランド式サウナ」「ご同伴いただけません」（ペット）「無料Wi-Fi」。SHIRO は「ウッドデッキ利用可能（21時～8時は屋外利用禁止）」（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://asnova-resort.com/noie-hakone/houses/shirosuite/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://asnova-resort.com/noie-hakone/houses/shirosuite/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://asnova-resort.com/noie-hakone/houses/shirosuite/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://asnova-resort.com/noie-hakone/houses/shirosuite/"}}},

    "140": {"name": "ルクス箱根湯本 LUX HAKONE YUMOTO",
            "reason": "FAQ「プールがサウナ後の水風呂としてご利用頂けます」→coldbath=pool、「ベンチが2脚あり、4名様のご利用が最適です」→sauna_cap=4、「プールやサウナのご利用は21時までとなります」→sauna_hours=limited、「トイレトレーニングとしつけのできた犬のみ」（小型犬2匹または大型犬1頭まで無料）、「高速無制限の光ケーブル・インターネットを無料でご利用いただけます」（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://lux-hakone.com/faq/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://lux-hakone.com/faq/"},
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://lux-hakone.com/faq/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://lux-hakone.com/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://lux-hakone.com/faq/"}}},

    "141": {"name": "koti hakone",
            "reason": "公式（vacation-koti.jp）はJS描画で本文が取れないため貸別荘予約サイトを出典とする。「IHコンロ」「ペットOK」（小型犬5匹まで、1匹1泊3,000円）。調査中に「P's Wood 箱根仙石原」の詳細情報が出たが施設名を確認して別施設と判断し不採用とした（2026-08確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://www.cottagelife.jp/kanagawa/la141600/id67096.html"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://www.cottagelife.jp/kanagawa/la141600/id67096.html"}}},
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
