#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, json, re, sys

AT = "2026-07"
s = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL).group(1))

def txt(v):
    return (v.get("desc") or "") + " " + (v.get("feature") or "")

NEG = re.compile(r"(なし|ありません|ございません|不可|非対応)")

def has(t, pat, w=12):
    for m in re.finditer(pat, t):
        if not NEG.search(t[m.end():m.end() + w]):
            return True
    return False

out, count = {}, {}

def put(vid, key, val):
    out.setdefault(vid, {})[key] = val
    count[key] = count.get(key, 0) + 1

for v in villas:
    vid = str(v["id"])
    t = txt(v)
    tags = v.get("tags") or []

    cap = str(v.get("capacity") or "").strip()
    if re.match(r"^\d+$", cap):
        put(vid, "capacity", int(cap))

    if "sauna" in tags:
        put(vid, "sauna_exists", "yes")
    if "pet" in tags:
        put(vid, "pet_ok", "yes")

    types = []
    for k, p in (("hut", r"サウナ小屋|屋外サウナ|離れのサウナ|独立したサウナ"),
                 ("barrel", r"バレルサウナ|樽型"),
                 ("tent", r"テントサウナ"),
                 ("indoor", r"室内サウナ|屋内サウナ")):
        if re.search(p, t):
            types.append(k)
    if len(types) == 1:
        put(vid, "sauna_type", types[0])

    wood = bool(re.search(r"薪スト|薪サウナ|薪の", t))
    elec = bool(re.search(r"電気スト|電気サウナ|HARVIA|Harvia|ハルビア|IKI", t))
    if wood and not elec:
        put(vid, "stove", "wood")
    elif elec and not wood:
        put(vid, "stove", "electric")

    if has(t, r"セルフロウリュ"):
        put(vid, "loyly", "yes")
    if has(t, r"チラー"):
        put(vid, "chiller", "yes")

    if has(t, r"水風呂"):
        put(vid, "coldbath", "bath")
    elif has(t, r"天然の水風呂|川に入|湖に入|川へ飛び込|湖へ飛び込"):
        put(vid, "coldbath", "river")

    if has(t, r"外気浴"):
        put(vid, "outdoor_rest", "yes")
    if has(t, r"Wi-?Fi|ワイファイ|無線LAN"):
        put(vid, "wifi", "yes")

lines = []
for vid in sorted(out, key=lambda x: int(x)):
    f = out[vid]
    keys = sorted(f)
    w = max(len(k) for k in keys) + 1
    rows = []
    for k in keys:
        val = f[k] if isinstance(f[k], int) else "'%s'" % f[k]
        rows.append("    %-*s { v: %s, src: 'desk', at: '%s' }" % (w, k + ":", val, AT))
    lines.append("")
    lines.append('  "%s": {' % vid)
    lines.append(",\n".join(rows))
    lines.append("  },")

io.open("out/spec-data-desk.js", "w", encoding="utf-8").write(
    "/* チャネルB 第一段：desc/feature/tags から抽出（%s） */\n" % AT
    + "\n".join(lines) + "\n")

print("=== 抽出結果 ===")
for k in sorted(count, key=lambda x: -count[x]):
    print("  %-14s %3d 件" % (k, count[k]))
print("\n対象施設: %d 件 / 総フィールド %d 個" % (len(out), sum(count.values())))
