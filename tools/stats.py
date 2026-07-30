import io, json, re, collections

geo = json.load(io.open("out/geo_places.json", encoding="utf-8"))
src = io.open("out/spec-data-auto.js", encoding="utf-8").read()
html = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", html, re.DOTALL).group(1))
names = dict((str(v["id"]), v.get("name", "")) for v in villas)

blocks = re.findall(r'"(\d+)": \{(.*?)\n  \},', src, re.DOTALL)
data = {}
for vid, body in blocks:
    f = {}
    for k, val in re.findall(r"(\w+):\s+\{ v: (.+?), src:", body):
        f[k] = val.strip("'")
    data[vid] = f

print("=== 掲載件数 ===")
print("  施設: %d / 286" % len(data))
for k in ("elevation", "supermarket", "conveni", "ic", "station", "onsen"):
    print("  %-12s %d 件" % (k, sum(1 for f in data.values() if k in f)))

def nums(k):
    out = []
    for vid, f in data.items():
        if k not in f:
            continue
        v = f[k].strip()
        m = re.search(r"(\d+)\s*分\s*$", v) or re.match(r"^(\d+)$", v)
        if m:
            out.append((int(m.group(1)), vid))
    return sorted(out)

print("\n=== 分布 ===")
for k, unit in (("elevation", "m"), ("supermarket", "分"), ("conveni", "分"),
                ("ic", "分"), ("station", "分"), ("onsen", "分")):
    a = nums(k)
    if not a:
        continue
    v = [x[0] for x in a]
    print("  %-12s 最小 %4d / 中央 %4d / 最大 %4d %s"
          % (k, v[0], v[len(v) // 2], v[-1], unit))

print("\n=== 要確認（極端な値）===")
warn = 0
for k, lim, label in (("supermarket", 45, "スーパー"), ("conveni", 35, "コンビニ"),
                      ("onsen", 60, "温泉"), ("elevation", 2500, "標高")):
    for val, vid in nums(k):
        if val > lim:
            print("  %-8s %5s  id=%-4s %s" % (label, val, vid, names.get(vid, "")[:28]))
            warn += 1
if not warn:
    print("  なし")

print("\n=== 座標の重複（別施設が同じ地点を指していないか）===")
pos = collections.defaultdict(list)
for vid, g in geo.items():
    pos["%.5f,%.5f" % (g["lat"], g["lng"])].append(vid)
dup = [(k, v) for k, v in pos.items() if len(v) > 1]
if not dup:
    print("  なし")
for k, v in sorted(dup, key=lambda x: -len(x[1]))[:12]:
    print("  %s : %s" % (k, " / ".join("%s(%s)" % (i, names.get(i, "")[:16]) for i in v)))
