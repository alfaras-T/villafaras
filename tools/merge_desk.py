#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, json, re, sys

SRCS = sys.argv[1:] or ["out/spec-data-desk.js"]
DATA = "spec-data.js"

def parse(text):
    out = {}
    for vid, blk in re.findall(r'"(\d+)":\s*\{(.*?)\n\s*\}', text, re.DOTALL):
        f = {}
        for k, v in re.findall(r"(\w+):\s*(\{[^}]*\})", blk):
            f[k] = " ".join(v.split())
        if f:
            out[vid] = f
    return out

cur = io.open(DATA, encoding="utf-8").read()
head = cur[:cur.index("window.VILLAFARAS_SPEC = {")]
existing = parse(re.sub(r"/\*.*?\*/", "", cur, flags=re.DOTALL))
desk = {}
for src in SRCS:
    for vid, f in parse(io.open(src, encoding="utf-8").read()).items():
        desk.setdefault(vid, {}).update(f)
print("読み込み: %s" % ", ".join(SRCS))

merged, added, skipped = {}, 0, 0
for vid in set(list(existing) + list(desk)):
    f = dict(existing.get(vid, {}))
    for k, v in (desk.get(vid) or {}).items():
        if k in f:
            skipped += 1
        else:
            f[k] = v
            added += 1
    merged[vid] = f
print("追加 %d フィールド / 既存を優先して見送り %d" % (added, skipped))

html = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", html, re.DOTALL).group(1))
names = dict((str(v["id"]), v.get("name", "")) for v in villas)

ORDER = ["sauna_exists", "sauna_type", "stove", "sauna_temp", "sauna_cap", "loyly",
         "heat_time", "sauna_hours", "coldbath", "chiller", "water_temp", "water_src",
         "water_depth", "outdoor_rest", "rest_chair", "villa_type", "neighbor_dist",
         "kitchen_type", "kitchen_burners", "bbq_roof", "firepit",
         "capacity", "comfort_cap", "pet_ok", "steps", "wifi",
         "elevation", "supermarket", "conveni", "ic", "station", "onsen"]
def ko(k):
    return (ORDER.index(k), k) if k in ORDER else (len(ORDER), k)

out = [head + "window.VILLAFARAS_SPEC = {"]
for vid in sorted(merged, key=lambda x: int(x)):
    f = merged[vid]
    if not f:
        continue
    keys = sorted(f, key=ko)
    w = max(len(k) for k in keys) + 1
    rows = ["    %-*s %s" % (w, k + ":", f[k]) for k in keys]
    nm = names.get(vid, "")
    out.append("")
    out.append('  "%s": {%s' % (vid, ("  /* %s */" % nm) if nm else ""))
    out.append(",\n".join(rows))
    out.append("  },")
out[-1] = out[-1].rstrip(",")
out.append("};")
io.open(DATA, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("%s を更新しました（%d 施設）" % (DATA, len(merged)))
