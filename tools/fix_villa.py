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
    "249": {"name": "グラン熱川",
            "reason": "公式サイトが存在しないため民泊仲介サイトを出典とする。「本格的なサウナと水風呂も完備」「最大定員:16」「ペットとの宿泊はできません。」「ワイヤレスインターネット」。capacity=9 は OTA の定員欄由来とみられ、独立した2つの仲介サイトが16で一致するためそちらを採る（公式での裏取りは未了）（2026-08確認）",
            "set_villa": {"capacity": "16"},
            "set_spec": {
                         "capacity": {"v": 16, "src": "desk", "at": "2026-08",
                                        "url": "https://sumasute.jp/shizuoka/12056"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://sumasute.jp/shizuoka/12056"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://sumasute.jp/shizuoka/12056"}}},

    "255": {"name": "貸別荘「碧 ai」",
            "reason": "「6名で入れるサウナルーム」「ロウリュができる本格サウナ室」（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 6, "src": "desk", "at": "2026-08",
                                         "url": "https://www.ai-inc.net/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://www.ai-inc.net/"}}},

    "256": {"name": "パーパスリゾート EG Sky Terrace 熱川",
            "reason": "「水風呂は3×7mの特大プールを利用」→coldbath=pool、「無料Wi-Fi」。サウナ80度・水風呂12度はサウナイキタイ由来で独立2回一致（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://www.purposeresort.com/atagawa"},
                         "water_temp": {"v": "t1015", "src": "desk", "at": "2026-08",
                                          "url": "https://www.purposeresort.com/atagawa"},
                         "sauna_temp": {"v": 80, "src": "desk", "at": "2026-08",
                                          "url": "https://www.purposeresort.com/atagawa"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.purposeresort.com/atagawa"}}},

    "258": {"name": "ALIVIO LUXE",
            "reason": "「ペット同伴は禁止です」「ガスコンロ」（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://alivio-stay.jp/luxe-ogi/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://alivio-stay.jp/luxe-ogi/"}}},

    "261": {"name": "Earthboat Minakami Fujiwara",
            "reason": "各棟に「水風呂・温泉露天風呂」を完備、「インフィニティチェア」「IHコンロ」「Wi-Fi」完備（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://earthboat.jp/minakami_fujiwara"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/minakami_fujiwara"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://earthboat.jp/minakami_fujiwara"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://earthboat.jp/minakami_fujiwara"}}},

    "262": {"name": "Earthboat Minakami Hodaigi",
            "reason": "「インフィニティチェア」「IHコンロ」「Wi-Fi」完備。サウナ90度・水風呂15度はサウナイキタイ由来で独立2回一致（2026-08確認）",
            "set_spec": {
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/minakami_hodaigi"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://earthboat.jp/minakami_hodaigi"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://earthboat.jp/minakami_hodaigi"},
                         "sauna_temp": {"v": 90, "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/minakami_hodaigi"},
                         "water_temp": {"v": "t1015", "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/minakami_hodaigi"}}},

    "268": {"name": "ポーラーハウス南軽井沢1",
            "reason": "pet_ok=yes は出典ありで正しいが、ペットタグが欠けていた。公式の建物一覧に「犬同伴：可　ドッグランあり　120㎡」とある（2026-08確認）",
            "add_tags": ["pet"]},

    "269": {"name": "THE LOOKOUT KUSATSU",
            "reason": "「Max70度の1人用サウナを完備！遠赤外線でしっかり汗をかけます！」より sauna_cap=1。既存の pet_ok=yes は出典ありだがペットタグが欠けていたので付与する（2026-08確認）",
            "add_tags": ["pet"],
            "set_spec": {
                         "sauna_cap": {"v": 1, "src": "desk", "at": "2026-08",
                                         "url": "https://travel.yahoo.co.jp/00921891/"}}},

    "270": {"name": "COCO VILLA 長瀞",
            "reason": "諸元表「サウナ収容人数 4名」「チラー ✕」「Colemanインフィニティチェア（2台）」「ガスコンロ3口」「Wi-Fi ◯」「セルフロウリュ」、および「ペットと一緒に宿泊できない施設」（2026-08確認）",
            "set_spec": {
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "chiller": {"v": "no", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://coco-villa.jp/villa/nagatoro/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://coco-villa.jp/villa/nagatoro/"}}},

    "271": {"name": "Earthboat Saitama Kawajima",
            "reason": "「インフィニティチェア」「ガスコンロ」「定員 4名」「種類・大きさ・頭数の制限なし」（ペット）「Wi-Fi」。同ブランドでもキッチンは拠点差があり、みなかみ2拠点=IH に対し川島=ガス（2026-08確認）",
            "set_villa": {"capacity": "4"},
            "set_spec": {
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://earthboat.jp/saitama_kawajima"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                            "url": "https://earthboat.jp/saitama_kawajima"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-08",
                                        "url": "https://earthboat.jp/saitama_kawajima"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                      "url": "https://earthboat.jp/saitama_kawajima"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://earthboat.jp/saitama_kawajima"}}},

    "273": {"name": "HOLE37",
            "reason": "「完全貸切のロウリュ付きサウナ」「ペット：不可」「wi-fiが利用可能です」。公式 hole37.com は JS描画で本文取得不可（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://www.ikyu.com/00051662/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/00051662/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.ikyu.com/00051662/"}}},

    "276": {"name": "COCO VILLA 大洗",
            "reason": "設備一覧が○✕の列挙形式で「愛犬同伴 ✕」「ドッグラン ✕」「焚き火 ✕」と明記されており、pet_ok=yes は誤り。ペットタグも外す。あわせて諸元表より「チラー madsaunist／SUPER ICE CHILLER」「サウナ収容人数 8名」「セルフロウリュ ◯」「Colemanインフィニティチェア（2台）」「キッチン（IHコンロ3口）」「Wi-Fi ◯」、水風呂は「ジャグジー（水/湯利用可能）」で兼用のため coldbath=tub（2026-08確認）",
            "remove_tags": ["pet"],
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/oarai/"},
                         "chiller": {"v": "yes", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/oarai/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://coco-villa.jp/villa/oarai/"},
                         "sauna_cap": {"v": 8, "src": "desk", "at": "2026-08",
                                         "url": "https://coco-villa.jp/villa/oarai/"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://coco-villa.jp/villa/oarai/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://coco-villa.jp/villa/oarai/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://coco-villa.jp/villa/oarai/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://coco-villa.jp/villa/oarai/"},
                         "firepit": {"v": "no", "src": "desk", "at": "2026-08",
                                       "url": "https://coco-villa.jp/villa/oarai/"}}},
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
