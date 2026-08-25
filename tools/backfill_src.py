#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""既存優先マージで失われた出典（url / at）を desk-research.js から埋め戻す。

merge_desk.py は既存値がある項目をスキップする。このとき値が同じであっても
候補側の url と at は捨てられるため、spec-data.js 側は「裏取り済みなのに
出典が無い」状態になる。その結果、初期の一括投入で入った値と、調べた結果
たまたま同じ値だった項目とが区別できなくなる。

  例: sauna_exists=yes は spec-data.js に235件あるが出典URLは1件も無い。
      うち93件は desk-research.js に出典付きで yes と記録されていた。

このツールは**値が一致している項目に限り** url と at を書き足す。
値は一切変更しない。値が食い違う項目は validate.py の食い違い検査の担当。

  python3 tools/backfill_src.py --dry-run
  python3 tools/backfill_src.py
  python3 tools/backfill_src.py --only sauna_exists
"""
import io, re, sys

DATA = "spec-data.js"
SRC = "data/desk-research.js"

DRY = "--dry-run" in sys.argv
ONLY = None
if "--only" in sys.argv:
    ONLY = sys.argv[sys.argv.index("--only") + 1]


def blank_comments(text):
    """コメントを空白に置換する。改行を残すので文字位置が保たれる。"""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "'\"":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def cells(path):
    """vid -> {key: {v, url, at}} を返す。"""
    s = blank_comments(io.open(path, encoding="utf-8").read())
    out = {}
    for vid, blk in re.findall(r'"(\d+)"\s*:\s*\{(.*?)\n\s*\}', s, re.DOTALL):
        d = out.setdefault(vid, {})
        for k, body in re.findall(r"(\w+):\s*\{([^}]*)\}", blk):
            mv = re.search(r"v:\s*('([^']*)'|[-\d.]+|true|false)", body)
            if not mv:
                continue
            d.setdefault(k, {
                "v": mv.group(1).strip("'"),
                "url": (re.search(r"url:\s*'([^']*)'", body) or [None, None])[1],
                "at": (re.search(r"at:\s*'([^']*)'", body) or [None, None])[1],
            })
    return out


spec, desk = cells(DATA), cells(SRC)
text = io.open(DATA, encoding="utf-8").read()

todo = []
for vid, f in spec.items():
    for k, c in f.items():
        if ONLY and k != ONLY:
            continue
        d = desk.get(vid, {}).get(k)
        if not d or not d["url"] or c["url"]:
            continue
        if str(c["v"]) != str(d["v"]):
            continue          # 値が違うものは埋め戻しの対象外
        todo.append((vid, k, d["url"], d["at"], c["at"]))

print("埋め戻し対象: %d 件%s" % (len(todo), ("（--only %s）" % ONLY) if ONLY else ""))
by_key = {}
for vid, k, _u, _a, _oa in todo:
    by_key[k] = by_key.get(k, 0) + 1
for k, n in sorted(by_key.items(), key=lambda x: -x[1]):
    print("   %-16s %3d 件" % (k, n))

changed = 0
for vid, key, url, at, old_at in todo:
    m = re.search(r'(^  "%s": \{.*?\n  \},?)' % vid, text, re.M | re.S)
    if not m:
        print("  !! id=%s のブロックが見つかりません" % vid); continue
    blk = m.group(1)
    mk = re.search(r"(\n\s*%s:\s*)(\{[^}]*\})" % re.escape(key), blk)
    if not mk:
        print("  !! id=%s の %s が見つかりません" % (vid, key)); continue
    body = mk.group(2)
    if "url:" in body:
        continue
    new = body[:-1].rstrip().rstrip(",")
    if at and "at:" in body:
        new = re.sub(r"at:\s*'[^']*'", "at: '%s'" % at, new)
    elif at:
        new += ", at: '%s'" % at
    new += ", url: '%s' }" % url
    text = text.replace(blk, blk.replace(mk.group(0), mk.group(1) + new, 1), 1)
    changed += 1

if DRY:
    print("\n[dry-run] %d 件を書き換え予定（値は変更しません）" % changed)
else:
    io.open(DATA, "w", encoding="utf-8").write(text)
    print("\n%s を更新しました（%d 件に出典を追加）" % (DATA, changed))
    print("値は変更していません。tools/validate.py で総フィールド数が変わらないことを確認してください。")
