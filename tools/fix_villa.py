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
            "reason": "early_late を early_checkin / late_checkout に分割。**この施設が分割の必要性を最もはっきり示した。** 旧 early_late は yes だったが、実際にはアーリーが明示的に不可だった。公式「アーリーチェックインは現在行っておりません。ご了承ください。」／「有料でレイトチェックアウトもご用意しております。」「有料オプションレイトチェックアウト：1時間あたり＋ご利用料代金の10％、最大2時間（12時まで）」。**1項目の可/不可では『レイトのみ可』を表現できず、yes がアーリー不可を隠していた**（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/sea-by-toramii/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://toramii.jp/sea-by-toramii/"}}},

    "17": {"name": "the MELLOW HOUSE 館山",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「※有料オプションにて、アーリーチェックイン・レイトチェックアウトも可能です。詳細は公式LINEにてお問合せください。」（1文で両方に言及）（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.mellowhouse.jp/question/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.mellowhouse.jp/question/"}}},

    "18": {"name": "On the wave 館山",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「15時チェックイン、10時チェックアウトです。※オプションでアーリーチェックイン、レイトチェックアウトに対応可能です。」（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://otw-tateyama.com/qa/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://otw-tateyama.com/qa/"}}},

    "21": {"name": "UMInoTERRACE",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「チェックイン 15:00~ （アーリーチェックインをご希望の方は13:00〜可能 別途15000円請求させて頂きます。」→early_checkin=yes。**late_checkout は入れない**: 同ページの「チェックアウト時間が遅れてしまった場合、30分毎に¥5,000請求させていただきますのでご注意ください。」は**超過時の延滞金の注意書きであってレイトチェックアウトの提供ではない**。他施設のような予約制オプションとしての明記が無い（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://piyo-terrace.com/vacationrentals/uminoterrace-villa/"}}},

    "33": {"name": "and RIVER勝浦",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「チェックイン PM 15:00 チェックアウト AM 11:00 アーリーチェックイン レイトチェックアウト [有料・応相談]」。id=60 と一字一句同じ文言で、同ブランドの共通テンプレートだが両施設の別ドメインで実在を確認済み（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.andriver-katsuura.com/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.andriver-katsuura.com/"}}},

    "34": {"name": "Retreat Villa Aym",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「Q. アーリーチェックイン・レイトチェックアウトは可能ですか？ A. 当日の予約状況により対応可能な場合がございます。」「●アーリーチェックイン 1時間前：11,000円（税込）」「●レイトチェックアウト ※受付はチェックイン当日18時までとなります 1時間以内：11,000円（税込）」。id=33/60 と違い個別の料金体系を持つ独自コンテンツ（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://aym.wyes-resort.com/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://aym.wyes-resort.com/"}}},

    "43": {"name": "Montevan RESORT VILLA",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「チェックイン15:00〜20:00、チェックアウト10:00（追加料金にてアーリーチェックイン/レイトチェックアウトも可能）※但し、当日の予約状況によってはご希望に添えない可能性もございます」（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.montevan.com/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.montevan.com/"}}},

    "60": {"name": "and FOREST勝浦 竹の離れ",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「チェックイン PM 15:00 チェックアウト AM 11:00 アーリーチェックイン レイトチェックアウト [有料・応相談]」（id=33 と同文言）（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.takenohanare.com/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.takenohanare.com/"}}},

    "65": {"name": "THE NALU",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「①チェックイン（15:00〜20:00）…※アーリーチェックインをご希望の際は、事前にご相談ください」「④チェックアウト（〜11:00）…※レイトチェックアウトをご希望の際も、事前にご相談ください」と別々の項目で書かれている（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://the-nalu.com/information/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://the-nalu.com/information/"}}},

    "72": {"name": "VILLA LAGI",
            "reason": "early_late を early_checkin / late_checkout に分割。公式Q&A「アーリーチェックイン、アウトをご希望の場合は1時間延長につき10000円(6人まで)1人追加毎に＠1000円となります。事前予約、またはチェックイン時にお申し出ください。」**記録済みの出典（トップページ）にはこの記載が無く、サイト内の /qa/ にあった。出典URLも差し替える**（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.chiba-isumi-privatevilla.com/qa/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.chiba-isumi-privatevilla.com/qa/"}}},

    "78": {"name": "enico.Mt.Fuji Resort & Glamping",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「チェックアウト 8：00～10：00 ※レイトチェックアウトも可能ですが、３０分につき２０００円頂戴しております」→late_checkout=yes。**early_checkin は入れない**: FAQページ全文を確認したが「アーリーチェックイン」の語自体が存在しない。不記載は不可の根拠にならないので不明のままとする（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://enico-mount-fuji.com/frequently-asked-questions/"}}},

    "92": {"name": "VILLA SAISON FUJI",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「アーリーチェックイン・レイトチェックアウトに関して 申し訳ございませんが、アーリーチェックインもレイトチェックアウトも承っておりません。」と両方を明示的に否定している（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://villa-saison-fuji.com/faq/"},
                         "late_checkout": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://villa-saison-fuji.com/faq/"}}},

    "126": {"name": "御宿 憩（OYADO IKOI）",
            "reason": "early_late を early_checkin / late_checkout に分割。公式「・ Check-in: 16:00～ ・ Check-out time ～10:00 Please contact us for early check-in and late check-out.」（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://stay-japan.tokyo/en/ikoi/"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://stay-japan.tokyo/en/ikoi/"}}},

    "131": {"name": "LEVATA",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「アーリーチェックイン・レイトチェックアウトできますか？ 出来ません」と両方を明示的に否定（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://levata.jp/"},
                         "late_checkout": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://levata.jp/"}}},

    "191": {"name": "軽井沢 HOUSE VILLA",
            "reason": "early_late を early_checkin / late_checkout に分割。公式FAQ「チェックインの時間は16〜20時、チェックアウトは11時迄となります。…また、アーリーチェックインやレイトチェックアウトは利用状況に応じてご対応可能ですが、追加費用が発生致します。」（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "early_checkin": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://karuizawa-house-villa.com/faq"},
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://karuizawa-house-villa.com/faq"}}},

    "267": {"name": "MOOSKA DE STUBEN",
            "reason": "early_late を early_checkin / late_checkout に分割。公式の料金ページ「レイトチェックアウト 翌12:00まで利用可能 22,000円／組」→late_checkout=yes。**early_checkin は入れない**: 「早朝サウナ」27,500円/組というオプションはあるがこれはサウナのみの早朝利用で、施設全体のアーリーチェックインではない。**記録済みの出典（トップページ）はJS描画前が空で内容を持たず、実際の情報は /price と /faq にあった**（2026-09確認）",
            "remove_spec": ["early_late"],
            "set_spec": {
                         "late_checkout": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://mooska.jp/price"}}},
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
