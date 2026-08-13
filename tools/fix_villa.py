#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys

FIXES = {
    # --- 一部客室のみサウナ付き
    "281": {"name": "SPA＆ごはんゆるうむ",
            "reason": "「セルフロウリュ可能なサウナ又は岩盤浴付き客室あり」と公式に明記。サウナ付きは一部客室のみで、他に共用のタワーサウナ等4種がある（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://yuluumu.co.jp/"}}},
    "99":  {"name": "ハンズアウトドアリゾート",
            "reason": "テントサウナは「VILLAのお部屋のみ」（3,800円/組）でPAO・Residenceには無い。別にバレルサウナ（12,000円/組・時間枠制）を共用（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://glampicks.jp/glamping/g46375/"}}},

    # --- 共用サウナのみ。shared はトップの絞り込み対象外なので sauna タグも外す。
    "266": {"name": "温泉グランピングシマブルー",
            "reason": "全7棟の客室設備は温泉露天風呂。サウナは楓仙峡に面した独立施設「森のサウナ」を貸切で共用（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://shimablue.jp"}}},
    "168": {"name": "湯屋　やまざくら",
            "reason": "全6室の旅館で、サウナは露天風呂・内風呂と並ぶ「三つの貸切風呂」の一つ。2024年6月新設のプライベートサウナも貸切利用で客室内ではない（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://hakoneyamazakura.com"}}},
    "254": {"name": "伊豆グランヴィレッジ　グランピング",
            "reason": "「敷地内には、温泉に浸かれるつぼ湯や檜の香りが広がるフィンランド式サウナを併設」。予約制・90分3,980円の貸切オプションで、テント側はバス・トイレのみ（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://travel.rakuten.co.jp/HOTEL/184404/184404.html"}}},
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
