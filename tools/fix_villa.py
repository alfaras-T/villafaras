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
    "52": {"name": "緑邸～OHTAKI～",
           "reason": "sauna_type='tent' -> 'barrel' は c195be8 で訂正済み（公式「離れに本格的なバレルサウナが"
                     "楽しめる施設をご用意いたしました。」）。同じページに未設定のまま残っていた項目を拾う。"
                     "サウナ「サウナでじっくり汗をかいた後に、汗を流して檜の水風呂につかり、椅子に座り大多喜の"
                     "心地よい風にあたり整いましょう。」／写真キャプション「セルフローリュも可能」「外気浴スペース」／"
                     "【追加オプション】「バレルサウナ 檜製水風呂」→ loyly=yes, coldbath=bath, outdoor_rest=yes。"
                     "BBQ「お好きな食材を持ち込み、ご家族とバーベキューはいかがでしょうか。離れには屋根があるので、"
                     "多少の雨でも安心です。」→ bbq_roof=roof。"
                     "【アメニティ】バスタオル・ハンドタオル・シャンプー・コンディショナー・ボディソープ・歯ブラシ・ひげ剃り、"
                     "【調理器具等】「食器、調理器、調味料などはご自由にお使いください」→ bring_towel / bring_amenity / "
                     "bring_seasoning=ready。【施設設備】「無料Wi-Fi」→ wifi=yes。"
                     "あわせて feature の「テントサウナ」を「バレルサウナ」に直す（extract_b.py が sauna_type='tent' を"
                     "出した元がこの誤記）。"
                     "見送り: (1) サウナの別料金「※ご利用は別料金となります。お申し込みの際に、サウナのご利用をお伝えください」は"
                     "受け皿の項目がない。sauna_hours は「利用可能時間」であって申込要否の欄ではないので入れない。"
                     "(2) firewood_fee は BBQ が「食材と薪炭などをお持ちこみください」＝持参で、fee の incl/extra どちらでもない。"
                     "(3) rest_chair は「椅子に座り」だけで infinity/bench/chair のどれか判別できない（2026-08確認）",
           "old_desc": "人工芝の庭・BBQ・テントサウナ",
           "new_desc": "人工芝の庭・BBQ・バレルサウナ",
           "set_spec": {
               "sauna_type":      {"v": "barrel", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "loyly":           {"v": "yes", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "coldbath":        {"v": "bath", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "outdoor_rest":    {"v": "yes", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "bbq_roof":        {"v": "roof", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "bring_towel":     {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "bring_amenity":   {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "bring_seasoning": {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"},
               "wifi":            {"v": "yes", "src": "desk", "at": "2026-08",
                                   "url": "https://www.ryokutei.jp/facility"}}},

    "92": {"name": "VILLA SAISON FUJI",
           "reason": "capacity=9 は一休の「定員」欄（9名が仕様上限）由来の既定値で誤り。公式FAQ「最大定員は何名ですか？ "
                     "最大定員は24名です。ヴィラには3つの寝室があり、10名様までご利用可能です。別館も3つの寝室があり、"
                     "11名様(無料のお子様除く)以上のご予約でヴィラ＋別館をご利用頂けます。」、"
                     "「ご宿泊者以外の方は、施設内にお入りいただけません。最大利用人数も24名様までとなっております。」。"
                     "公式予約ページの諸元表も「定員 最大24名」、本文「追加でエクストラベッドやベビーベッドも設置可能で、"
                     "最大24名様までご宿泊頂けます。」。検索要約に出る10名/13名は本館ヴィラのみの利用可能人数（FAQの人数表で"
                     "1〜10名様＝ヴィラのみ、13〜14名様＝別館寝室2まで）であって施設の定員ではない。"
                     "DB の feature「最大24名が宿泊できる」desc「最大24名まで滞在できます」とも一致する。"
                     "「当施設は敷地内全体を一組限定で貸切りとなりますので、ヴィラ・別館すべて他のお客様とご一緒になることは"
                     "ありません。共有施設もなく、全施設、貸切となります。」なので棟別に代表値が割れる型でもない。"
                     "ついでに stove='wood' も誤り。FAQ「サウナで使用するストーブと燃料は何ですか？ 電気ストーブです。」で、"
                     "薪ストーブは客室の暖房（「薪ストーブとファイアーピットで使う薪は、無料でご用意しております。」）。"
                     "desc の「薪ストーブを備え」を extract_b.py が拾って入れた値とみられる。"
                     "同FAQから loyly=yes（「ロウリュウは出来ますか？ 可能です。」）、"
                     "sauna_hours=limited（「近隣にご配慮いただくため、プールやサウナのご利用は21時までとなります。」）、"
                     "early_late=no（「アーリーチェックインもレイトチェックアウトも承っておりません。」）、"
                     "firewood_fee=incl・firepit=stand（上記の薪無料とファイアーピット）、"
                     "fee_bbq=incl（「簡単な操作で着火できるガスグリルを備えており、自由にご使用いただけます。炭や燃料などの"
                     "ご持参は不要です。」）、fee_pet=0（「ペットは無料でご宿泊いただけます。」）、"
                     "bring_towel / bring_amenity=ready（「・バスタオル／フェイスタオル ・バスローブ ・パジャマ ・シャンプー、"
                     "コンディショナー…」）、bring_seasoning=ready（「塩、コショウ、オリーブオイル、醤油、バター。」）、"
                     "wifi=yes（「高速無制限の光ケーブル・インターネットを無料でご利用いただけます」）。"
                     "見送り: (1) coldbath は「秋・冬はサウナの水風呂としてご利用ください」（プール）"
                     "「サウナの際には水風呂としてもご利用頂けます」（ジャグジー）で、CLAUDE.md に既知のプール兼用の選択肢が"
                     "ない型（これで10件目）。(2) villa_type はヴィラ＋別館の2棟だが一組貸切なので solo とも multi とも"
                     "決められない。チェックイン15:00〜18:00・チェックアウト11:00 は既存値と一致（2026-08確認）",
           "set_villa": {"capacity": "24"},
           "set_spec": {
               "capacity":        {"v": 24, "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "stove":           {"v": "electric", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "loyly":           {"v": "yes", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "sauna_hours":     {"v": "limited", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "early_late":      {"v": "no", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "firepit":         {"v": "stand", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "firewood_fee":    {"v": "incl", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "fee_bbq":         {"v": "incl", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "fee_pet":         {"v": 0, "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "bring_towel":     {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "bring_amenity":   {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "bring_seasoning": {"v": "ready", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"},
               "wifi":            {"v": "yes", "src": "desk", "at": "2026-08",
                                   "url": "https://villa-saison-fuji.com/faq/"}}},
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
