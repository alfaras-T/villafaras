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
    "188": {"name": "COCO VILLA 軽井沢",
            "reason": "**stove=electric は正しい。出典を付ける。** COCO VILLA は施設ごとに構造化されたスペック欄を持っており、「方式：電気式サウナ」と明記したうえで、ハウスルールにも「COCO VILLA 軽井沢 のサウナには『電気』を使用します。」とある。サウナストーブの銘柄は「MISA」。**ブランド5施設で銘柄が MISA / HARVIA / ブロスサウナ / NARVI / 記載なし とばらけており、文面の使い回しではなく施設ごとに書き分けられている。** とくに伊豆赤沢は銘柄が HARVIA だが方式欄で電気と明記されており、**メーカー名だけでは決まらないが方式欄があれば決まる**という好例（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/karuizawa/"}}},

    "234": {"name": "COCO VILLA 伊豆赤沢",
            "reason": "**stove=electric は正しい。出典を付ける。** COCO VILLA は施設ごとに構造化されたスペック欄を持っており、「方式：電気式サウナ」と明記したうえで、ハウスルールにも「COCO VILLA 伊豆赤沢 のサウナには『電気』を使用します。」とある。サウナストーブの銘柄は「HARVIA（ハルビア）」。**ブランド5施設で銘柄が MISA / HARVIA / ブロスサウナ / NARVI / 記載なし とばらけており、文面の使い回しではなく施設ごとに書き分けられている。** とくに伊豆赤沢は銘柄が HARVIA だが方式欄で電気と明記されており、**メーカー名だけでは決まらないが方式欄があれば決まる**という好例（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/izuakazawa/"}}},

    "235": {"name": "COCO VILLA 大室山",
            "reason": "**stove=electric は正しい。出典を付ける。** COCO VILLA は施設ごとに構造化されたスペック欄を持っており、「方式：電気式サウナ」と明記したうえで、ハウスルールにも「COCO VILLA 大室山 のサウナには『電気』を使用します。」とある。サウナストーブの銘柄は「ブロスサウナ」。**ブランド5施設で銘柄が MISA / HARVIA / ブロスサウナ / NARVI / 記載なし とばらけており、文面の使い回しではなく施設ごとに書き分けられている。** とくに伊豆赤沢は銘柄が HARVIA だが方式欄で電気と明記されており、**メーカー名だけでは決まらないが方式欄があれば決まる**という好例（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/omuroyama/"}}},

    "270": {"name": "COCO VILLA 長瀞",
            "reason": "**stove=electric は正しい。出典を付ける。** COCO VILLA は施設ごとに構造化されたスペック欄を持っており、「方式：電気式サウナ」と明記したうえで、ハウスルールにも「COCO VILLA 長瀞 のサウナには『電気』を使用します。」とある。サウナストーブの銘柄は「NARVI」。**ブランド5施設で銘柄が MISA / HARVIA / ブロスサウナ / NARVI / 記載なし とばらけており、文面の使い回しではなく施設ごとに書き分けられている。** とくに伊豆赤沢は銘柄が HARVIA だが方式欄で電気と明記されており、**メーカー名だけでは決まらないが方式欄があれば決まる**という好例（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/nagatoro/"}}},

    "276": {"name": "COCO VILLA 大洗",
            "reason": "**stove=electric は正しい。出典を付ける。** COCO VILLA は施設ごとに構造化されたスペック欄を持っており、「方式：電気式サウナ」と明記したうえで、ハウスルールにも「COCO VILLA 大洗 のサウナには『電気』を使用します。」とある。サウナストーブの銘柄は「記載なし」。**ブランド5施設で銘柄が MISA / HARVIA / ブロスサウナ / NARVI / 記載なし とばらけており、文面の使い回しではなく施設ごとに書き分けられている。** とくに伊豆赤沢は銘柄が HARVIA だが方式欄で電気と明記されており、**メーカー名だけでは決まらないが方式欄があれば決まる**という好例（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://coco-villa.jp/villa/oarai/"}}},

    "122": {"name": "Earthboat Nasu",
            "reason": "**stove=wood は正しい。出典を付ける。** 設備欄「サウナ：フィンランド式サウナ（薪ストーブ）」＋本文「自分で薪をくべて温めるサウナ」。**Earthboat の5施設は wood 4件・electric 1件に分かれているが、これは投入時の誤りではなく実態差だった。** Saitama Kawajima だけが公園内のグランピング型で、他4施設（山間部の一棟貸し型）とはコンセプトが異なり、公式も明確に書き分けている（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/nasu"}}},

    "195": {"name": "Earthboat Kurohime",
            "reason": "**stove=wood は正しい。出典を付ける。** 設備欄「サウナ：フィンランド式サウナ（薪ストーブ）」＋本文「自分で薪をくべて温めるサウナ」。**Earthboat の5施設は wood 4件・electric 1件に分かれているが、これは投入時の誤りではなく実態差だった。** Saitama Kawajima だけが公園内のグランピング型で、他4施設（山間部の一棟貸し型）とはコンセプトが異なり、公式も明確に書き分けている（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/kurohime"}}},

    "261": {"name": "Earthboat Minakami Fujiwara",
            "reason": "**stove=wood は正しい。出典を付ける。** 設備欄「サウナ：フィンランド式サウナ（薪ストーブ）」＋本文「自分で薪をくべて温めるサウナ」。**Earthboat の5施設は wood 4件・electric 1件に分かれているが、これは投入時の誤りではなく実態差だった。** Saitama Kawajima だけが公園内のグランピング型で、他4施設（山間部の一棟貸し型）とはコンセプトが異なり、公式も明確に書き分けている（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_fujiwara"}}},

    "262": {"name": "Earthboat Minakami Hodaigi",
            "reason": "**stove=wood は正しい。出典を付ける。** 設備欄「サウナ：フィンランド式サウナ（薪ストーブ）」＋本文「自分で薪をくべて温めるサウナ」。**Earthboat の5施設は wood 4件・electric 1件に分かれているが、これは投入時の誤りではなく実態差だった。** Saitama Kawajima だけが公園内のグランピング型で、他4施設（山間部の一棟貸し型）とはコンセプトが異なり、公式も明確に書き分けている（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://earthboat.jp/minakami_hodaigi"}}},

    "271": {"name": "Earthboat Saitama Kawajima",
            "reason": "**stove=electric は正しい。出典を付ける。** 拠点の特徴「…電気ストーブサウナ」＋設備欄「サウナ：電気式サウナ」。**Earthboat の5施設は wood 4件・electric 1件に分かれているが、これは投入時の誤りではなく実態差だった。** Saitama Kawajima だけが公園内のグランピング型で、他4施設（山間部の一棟貸し型）とはコンセプトが異なり、公式も明確に書き分けている（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
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
