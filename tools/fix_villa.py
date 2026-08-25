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
    "230": {"name": "WEAZER西伊豆 廻",
            "reason": "客室Wi-Fi／木々に包まれたウッドデッキ・デイベッド2台（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.chillnn.com/ja/1836d2246923a9/room/198f05d15012dc"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.chillnn.com/ja/1836d2246923a9/room/198f05d15012dc"}}},

    "234": {"name": "COCO VILLA 伊豆赤沢",
            "reason": "諸元表「セルフロウリュ対応」「サウナ収容人数 4名」「水風呂収容人数 1名」「チラー ✕」「IHコンロ 2口」「Wi-Fi ◯」、および「COCO VILLA 伊豆赤沢はペットと一緒に宿泊できない施設」（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "chiller": {"v": "no", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/izuakazawa/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://coco-villa.jp/villa/izuakazawa/"}}},

    "235": {"name": "COCO VILLA 大室山",
            "reason": "諸元表「6名」（サウナ収容人数）「チラー ✕」「Coleman インフィニティチェア（2台）」「ガスコンロ3口」「12名」「愛犬同伴✕」「Wi-Fi ◯」（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "sauna_cap": {"v": 6, "src": "desk", "at": "2026-08",
                                         "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "chiller": {"v": "no", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/omuroyama/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://coco-villa.jp/villa/omuroyama/"}}},

    "236": {"name": "Tiny Base The MOUNTAiN",
            "reason": "「セルフロウリュ」対応、「ガスコンロ」搭載、Wi-Fi あり（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://tinybase.co.jp/stay/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://tinybase.co.jp/stay/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://tinybase.co.jp/stay/"}}},

    "237": {"name": "Tiny Base The Irita-hama",
            "reason": "「サウナはフィンランド式サウナストーブ（HARVIA社・電気式）」「インターネット接続(無線LAN形式)」（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://travel.rakuten.co.jp/HOTEL/197338/197338.html"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://travel.rakuten.co.jp/HOTEL/197338/197338.html"}}},

    "239": {"name": "AMAO VILLA",
            "reason": "「最高95℃まで楽しめる本格仕様のサウナ」（範囲表記のため上限を採用）「最大8名様までご一緒いただける広々とした作り」「心地よいクールダウンを叶える水風呂」「インフィニティチェア」「3口IHコンロ」（2026-08確認）",
            "set_spec": {
                         "sauna_temp": {"v": 95, "src": "desk", "at": "2026-08",
                                          "url": "https://www.amaovilla.com/amao-villa-futo/"},
                         "sauna_cap": {"v": 8, "src": "desk", "at": "2026-08",
                                         "url": "https://www.amaovilla.com/amao-villa-futo/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.amaovilla.com/amao-villa-futo/"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://www.amaovilla.com/amao-villa-futo/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://www.amaovilla.com/amao-villa-futo/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.amaovilla.com/amao-villa-futo/"}}},

    "240": {"name": "Wellリゾート富士",
            "reason": "FAQ「サウナはありますか？」→「ございます。※水風呂はございません」。水風呂を直接尋ねた設問への回答で範囲が一致するため否定値を記録できる。「ペット同伴でのご利用はご遠慮いただいております。（盲導犬、介助犬、聴導犬は除きます。）」（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "none", "src": "desk", "at": "2026-08",
                                        "url": "https://wellresort.jp/faq/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://wellresort.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://wellresort.jp/faq/"}}},

    "241": {"name": "Poolen ITO",
            "reason": "「本場フィンランドでも利用されているセルフロウリュも可能な本格的バレルサウナ」、プールをサウナ後のクールダウンに使用（冬は水風呂として活用）、「ガゼボーを始めとしたリラックスコンテンツ」「無料Wi-Fi」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://hi-nichijo.com/poolen/ito/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://hi-nichijo.com/poolen/ito/"},
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://hi-nichijo.com/poolen/ito/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://hi-nichijo.com/poolen/ito/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://hi-nichijo.com/poolen/ito/"}}},

    "242": {"name": "the villa Oka 伊豆高原温泉",
            "reason": "公式宿泊ガイド「フィンランドから直輸入したMISA製の電気ストーブ」「森に囲まれ、海を望むことができるバルコニー」「三口IHコンロ」「2つのSSIDが利用可能」（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://note.com/the_villa_oka/n/n1ff90d61d2c3"}}},

    "243": {"name": "Azure Palace 伊豆高原",
            "reason": "「お庭にテントサウナがございます。無料でご利用いただけます。」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                          "url": "https://azurepalace.net"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://azurepalace.net"}}},

    "244": {"name": "HAKU-AKAZAWA- 【波空】",
            "reason": "「温度14度前後」（水風呂）→ water_temp=t1015、「整いスペース」「座り心地の良い整い椅子と焚火」（2026-08確認）",
            "set_spec": {
                         "water_temp": {"v": "t1015", "src": "desk", "at": "2026-08",
                                          "url": "https://www.haku-resort.com/"},
                         "rest_chair": {"v": "chair", "src": "desk", "at": "2026-08",
                                          "url": "https://www.haku-resort.com/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.haku-resort.com/"}}},

    "245": {"name": "villa 緑と物語",
            "reason": "別棟「緑青(ろくしょう)の湯」にサウナ完備、クールダウンは「ジャグジーバス」＝兼用設備、「アウトドアリビングにはバイオエタノール暖炉が設置」（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://prtimes.jp/main/html/rd/p/000000001.000154491.html"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://prtimes.jp/main/html/rd/p/000000001.000154491.html"}}},

    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "「冬はサウナ後の水風呂としてプールをご活用ください」＝プール兼用（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://luxevillas-izu.com/stay/sana-izuomuroyama/"}}},
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
