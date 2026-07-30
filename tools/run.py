import io, json, os, re, subprocess, time, unicodedata
import urllib.parse
import channel_a as C

OUT = "out"
CACHE = os.path.join(OUT, "cache")
os.makedirs(CACHE, exist_ok=True)

src = os.path.join(OUT, "geo_places.json")
if not os.path.exists(src):
    raise SystemExit("out/geo_places.json がありません。先に places_geocode.py を実行してください。")
places_geo = json.load(io.open(src, encoding="utf-8"))
seed = {}
for vid, g in places_geo.items():
    seed[vid] = {"lat": g["lat"], "lng": g["lng"],
                 "matched": "(Places)", "hits": 1, "source": "existing"}
io.open(os.path.join(CACHE, "geo.json"), "w", encoding="utf-8").write(
    json.dumps(seed, ensure_ascii=False, indent=1))
print("Placesの座標 %d 件を読み込みました" % len(seed))


def no_geocode(addr):
    return None


def curl_json(url, data=None, timeout=90, retries=3):
    cmd = ["curl", "-fsSL", "--max-time", str(int(timeout)),
           "-H", "User-Agent: " + C.UA]
    if data is not None:
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded",
                "--data-binary", "@-"]
    cmd += [url]
    last = ""
    for i in range(retries):
        p = subprocess.run(cmd, input=data,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode == 0:
            return json.loads(p.stdout.decode("utf-8"))
        last = p.stderr.decode("utf-8", "replace")[:160]
        time.sleep(3 * (i + 1))
    raise IOError("curl: " + last)


NG_IC = re.compile(r"予定|計画|仮称|工事|建設")


def clean_name(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = s.replace("、", " ").replace("　", " ")
    return re.sub(r"\s+", " ", s).strip()


def overpass_candidates(lat, lng):
    parts = []
    for key, tag in C.OVERPASS_TAGS.items():
        parts.append('nwr%s(around:%d,%.6f,%.6f);'
                     % (tag, C.RADIUS[key], lat, lng))
    q = "[out:json][timeout:120];(%s);out center tags;" % "".join(parts)
    data = urllib.parse.urlencode({"data": q}).encode("utf-8")
    res = C.http_json("https://overpass-api.de/api/interpreter",
                      data=data, timeout=180)
    out = dict((k, []) for k in C.OVERPASS_TAGS)
    for el in res.get("elements", []):
        tags = el.get("tags", {})
        c = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
        if c.get("lat") is None or c.get("lon") is None:
            continue
        name = clean_name(tags.get("name") or tags.get("name:ja"))
        if tags.get("shop") == "supermarket":
            k = "supermarket"
        elif tags.get("shop") == "convenience":
            k = "conveni"
        elif tags.get("highway") == "motorway_junction":
            k = "ic"
            if not name or NG_IC.search(name):
                continue
        elif tags.get("railway") == "station":
            k = "station"
            if not name:
                continue
        elif tags.get("amenity") == "public_bath":
            k = "onsen"
        else:
            continue
        out[k].append({"name": name, "lat": c["lat"], "lng": c["lon"],
                       "km": round(C.haversine_km((lat, lng),
                                                  (c["lat"], c["lon"])), 2)})
    for k in out:
        out[k] = sorted(out[k], key=lambda x: x["km"])[:3]
    return out


_drive = C.driving_minutes


def driving_minutes(origin, candidates):
    best = _drive(origin, candidates)
    if best and best.get("min", 0) < 1:
        best["min"] = 1
    return best


C.http_json = curl_json
C.geocode = no_geocode
C.overpass_candidates = overpass_candidates
C.driving_minutes = driving_minutes
print("→ 座標はPlaces / 通信はcurl / 未開通ICは除外\n")
C.main()
