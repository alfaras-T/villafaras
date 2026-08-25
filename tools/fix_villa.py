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
    "229": {"name": "WEAZER西伊豆",
            "reason": "sauna_exists=yes は誤り。公式予約サイトのFAQ「サウナはありますか？」に「WEAZER Villaのお部屋にはサウナはございません。」と明記されている。同FAQは続けて「WEAZER 廻のお部屋には客室内にサウナ(定員2名・95℃)がございます。」とあり、サウナがあるのは別施設として登録されている id=230『WEAZER西伊豆 廻』のほう。DB住所（沼津市戸田2592-1）は Villa 側に対応する。no に訂正しサウナタグを外す（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {
                         "sauna_exists": {"v": "no", "src": "desk", "at": "2026-08",
                                            "url": "https://www.chillnn.com/ja/1836d2246923a9"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.chillnn.com/ja/1836d2246923a9"}}},

    "230": {"name": "WEAZER西伊豆 廻",
            "reason": "公式予約サイトのFAQに「WEAZER 廻のお部屋には客室内にサウナ(定員2名・95℃)がございます。」「\"完全オフグリッド\"の建物のため、1泊あたり2回(45分×2回)までのご利用とさせていただいております。」とあり、形式・定員・室温・利用制限が一度に確定した（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                          "url": "https://www.chillnn.com/ja/1836d2246923a9"},
                         "sauna_cap": {"v": 2, "src": "desk", "at": "2026-08",
                                         "url": "https://www.chillnn.com/ja/1836d2246923a9"},
                         "sauna_temp": {"v": 95, "src": "desk", "at": "2026-08",
                                          "url": "https://www.chillnn.com/ja/1836d2246923a9"},
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://www.chillnn.com/ja/1836d2246923a9"}}},

    "188": {"name": "COCO VILLA 軽井沢",
            "reason": "公式サイトが設備を表形式で持っており一度に確定できた。「敷地内には、COCO VILLAオリジナルの3Dプリンター製サウナを設置」→sauna_type=hut、「セルフロウリュ ◯」→loyly=yes、「サウナ収容人数 4名」→sauna_cap=4、「チラー ◯（COCO VILLA オリジナルチラー）」→chiller=yes、「キッチン（IHコンロ3口）」→kitchen_type=ih、「Wi-Fi ◯」→wifi=yes、「COCO VILLA 軽井沢はペットと一緒に宿泊できない施設」→pet_ok=no。チラーは11〜3月使用不可という季節制限があるがスキーマに記録先がない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-08",
                                          "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "chiller": {"v": "yes", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/karuizawa/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://coco-villa.jp/villa/karuizawa/"}}},

    "195": {"name": "Earthboat Kurohime",
            "reason": "公式に「インフィニティチェア」→rest_chair=infinity、「ガスコンロ」→kitchen_type=gas、Wi-Fi あり。既存の stove=wood（「フィンランド式サウナ（薪ストーブ）」）、coldbath=bath（「水風呂（一部客室は温水利用可）」＝専用の水風呂）、outdoor_rest=yes も再確認した（2026-08確認）",
            "set_spec": {
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/kurohime"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://earthboat.jp/kurohime"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://earthboat.jp/kurohime"}}},

    "211": {"name": "オーシャンテラスAtami",
            "reason": "公式に「1名用プライベートサウナと温泉を備えた」とあり sauna_cap=1。サウナ定員1名は本DBで最小（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 1, "src": "desk", "at": "2026-08",
                                         "url": "https://www.resolstay.jp/details/oceanterrace/"}}},

    "212": {"name": "熱海リゾート",
            "reason": "公式に「サウナは室内にある2名用です」→sauna_cap=2、「ペットの同伴は禁止」→pet_ok=no、「Wi-Fi環境あり」→wifi=yes。既存の sauna_type=indoor、coldbath=bath（「浴槽は二つあり、温泉と水風呂を行き来する本格的な\"ととのう体験\"も可能」＝温泉浴槽とは別の水風呂）も再確認（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 2, "src": "desk", "at": "2026-08",
                                         "url": "https://www.resolstay.jp/details/atamiresort/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.resolstay.jp/details/atamiresort/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.resolstay.jp/details/atamiresort/"}}},

    "221": {"name": "マイグレYEBISU",
            "reason": "公式に「本格的フィンランドサウナ…最大9名で利用可能」（サウナ室9.5㎡）とあり sauna_cap=9。宿泊定員も9名だが原文では別々に記載されており取り違えではない。「地下から汲み上げられた冷たい天然水」→water_src=well（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 9, "src": "desk", "at": "2026-08",
                                         "url": "https://www.maigre.jp/yebisu"},
                         "water_src": {"v": "well", "src": "desk", "at": "2026-08",
                                         "url": "https://www.maigre.jp/yebisu"}}},
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
