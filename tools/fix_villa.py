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
    "109": {"name": "Kakoi 雪嶺",
            "reason": "「スイッチをつけた後、2.5-3時間で90度近くまで上昇します」「同時に4名様までご利用いただけるプライベートサウナ」「隣接のインナーバルコニーで外気浴をご堪能ください」「ペット：不可」。ブランド公式トップの「相模湾を見下ろしながら薪火サウナ」は同ブランド別施設『蒼波』の紹介文とみられるため stove には採らない（2026-08確認）",
            "set_spec": {
                         "sauna_temp": {"v": 90, "src": "desk", "at": "2026-08",
                                          "url": "https://travel.yahoo.co.jp/00052459/info/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://travel.yahoo.co.jp/00052459/info/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://travel.yahoo.co.jp/00052459/info/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00052459/info/"}}},

    "111": {"name": "HOTEL SEION FUJI",
            "reason": "「定員：最大8名」「ペット：不可」「Wi-Fi：利用可能」。SAUNA BROS.WEB とYahoo!トラベル共通で「富士北麓の湧水を利用した造作内風呂と露天風呂」→water_src=spring、「お湯風呂と水風呂は四季に合わせて自由に切り替え可能」→同一浴槽の兼用なので coldbath=tub、「バルコニーでの外気浴」。既存の stove=electric は「ストーブはHARVIAのCILINDROを採用しています」（CILINDROは電気機種）で裏付けが取れた（2026-08確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://travel.yahoo.co.jp/00052607/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00052607/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://travel.yahoo.co.jp/00052607/"},
                         "water_src": {"v": "spring", "src": "desk", "at": "2026-08",
                                         "url": "https://travel.yahoo.co.jp/00052607/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://travel.yahoo.co.jp/00052607/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://travel.yahoo.co.jp/00052607/"}}},

    "112": {"name": "private villa ietona",
            "reason": "「ペットの連れ込みは固くお断りいたします」「扉を開ければ森の中での外気浴」。公式サイトはテキストが薄く一休が実質の情報源（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/00051713/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.ikyu.com/00051713/"}}},

    "137": {"name": "P's Wood 箱根仙石原",
            "reason": "公式「露天風呂、檜のバレルサウナ、広いダイニングテーブル」→sauna_type=barrel、「国産檜のサウナは4名が同時にご利用できますので、何度でも汗を流してください。」→sauna_cap=4、「星空を眺めながら入浴できる信楽焼の温泉露天風呂はサウナ後の水風呂としてもご活用いただけます。」→coldbath=tub（温泉露天との兼用）。楽天トラベル「ペットの同伴は禁止です」「インターネット接続(無線LAN形式)」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ps-wood.jp/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://www.ps-wood.jp/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ps-wood.jp/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ps-wood.jp/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.ps-wood.jp/"}}},

    "138": {"name": "Casablanca Villa Hakone",
            "reason": "公式「ヒノキサウナを完備」「温度：100度まで」（範囲は上限を採る）「人数：3-4名様」（サウナ室の収容人数。宿泊定員とは別）「テラスには五右衛門風呂を設置。サウナ後の水風呂としてご利用いただけます。お湯を入れれば露天風呂としてもお使いいただけます。」→coldbath=tub、「ペットの同伴はできません。」。インフィニティプールは38〜40℃の温水で水風呂には該当しない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                          "url": "https://casablancaworld.jp/villa-hakone/"},
                         "sauna_temp": {"v": 100, "src": "desk", "at": "2026-08",
                                          "url": "https://casablancaworld.jp/villa-hakone/"},
                         "sauna_cap": {"v": 4, "src": "desk", "at": "2026-08",
                                         "url": "https://casablancaworld.jp/villa-hakone/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://casablancaworld.jp/villa-hakone/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://casablancaworld.jp/villa-hakone/"}}},

    "147": {"name": "箱根芦ノ湖ゴルフヴィラ",
            "reason": "「ペット不可」「屋内はインターネット常時接続可能」「基本の調理器具/鍋/フライパン/食器＆カトラリー/電子レンジ/冷蔵庫/IHコンロ」「箱根の澄んだ空気の中での外気浴」。ストーブは「Harvia社製」の記載のみで薪／電気の別が特定できず入れない（Harviaは両方を製造）（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://tocovel.com/accommodation/hakone-golf/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://tocovel.com/accommodation/hakone-golf/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://tocovel.com/accommodation/hakone-golf/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://tocovel.com/accommodation/hakone-golf/"}}},

    "152": {"name": "NIWA　KAMAKURA",
            "reason": "公式「サウナストーンに水をかけて蒸気（ロウリュ）を出すことで湿度を上げる」「15:00〜21:00、9:00〜10:30までご利用可能」→sauna_hours=limited、「敷地内から湧き出る井戸水を使用」→water_src=well、「鎌倉石の洞窟や竹林を臨むユニークな外気浴スペース」。**水風呂の説明にある「深さ4.5m」は井戸の掘削深度であって水風呂の水深ではないため water_depth には採らない**（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://niwa-kamakura.jp/products/stay"},
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://niwa-kamakura.jp/products/stay"},
                         "water_src": {"v": "well", "src": "desk", "at": "2026-08",
                                         "url": "https://niwa-kamakura.jp/products/stay"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://niwa-kamakura.jp/products/stay"}}},

    "154": {"name": "LULLA",
            "reason": "「サウナ IN 15:00～24:00」→sauna_hours=limited、「ペット 不可 LULLAでは建物の特質上、ペットの同伴をお断りしております。」。サウナ形式は独立2回の検索で「BURROW製のバレルサウナ」と一致（BURROWは国産バレルサウナ専業メーカー）（2026-08確認）",
            "set_spec": {
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://www.ikyu.com/00052476/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/00052476/"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052476/"}}},

    "156": {"name": "MONS GORA",
            "reason": "sauna_exists=yes は実態と合わない。MONS GORA は SOLIS棟・LUNA棟の2棟構成で、一休のプラン名が「SOLIS棟サウナ付【素泊まり】350平米温泉付」、紹介文も「絶景を楽しむガラス張りの人気のサウナをSOLIS棟へ」。一方 LUNA棟は「LUNA棟には大涌谷温泉のかけ流し温泉の足湯を備えています。」でサウナの言及がない。一部の棟のみサウナ付きなので room に訂正する（room はサウナタグを維持）。**なお公式サイト・一休ページとも実機ブラウザでレンダラが応答せず、筆者自身による原文の再確認はできていない。根拠は上記のプラン名と紹介文の引用のみ**（2026-08確認）",
            "set_spec": {
                         "sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                            "url": "https://www.ikyu.com/00051646/"}}},

    "160": {"name": "雅・仙石原",
            "reason": "公式サイトが存在しないため掲載サイトを出典とする。「三口IHコロ」（原文ママ、コンロの誤植とみられる）「同伴不可」、Wi-Fi 明記。「最大14名様までご宿泊いただける広大な空間」で既存の capacity=14 も裏付けられた。温泉の「24時間ご利用可能」は温泉浴室の話でサウナの利用時間ではないため sauna_hours には採らない（2026-08確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://tripto.jp/facilities/575"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://tripto.jp/facilities/575"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://tripto.jp/facilities/575"}}},
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
