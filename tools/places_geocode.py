import csv, difflib, io, json, math, os, re, subprocess, sys, time, unicodedata
import urllib.parse

KEY = os.environ.get("GMAPS_KEY", "").strip()
if not KEY:
    raise SystemExit("環境変数 GMAPS_KEY が設定されていません")

OUT = "out"
os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(OUT, "places.json")
cache = {}
if os.path.exists(CACHE):
    try:
        cache = json.load(io.open(CACHE, encoding="utf-8"))
    except Exception:
        cache = {}


def save_cache():
    tmp = CACHE + ".tmp"
    io.open(tmp, "w", encoding="utf-8").write(
        json.dumps(cache, ensure_ascii=False, indent=1))
    os.replace(tmp, CACHE)


def run(cmd, data=None):
    p = subprocess.run(cmd, input=data,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise IOError(p.stderr.decode("utf-8", "replace")[:150])
    return json.loads(p.stdout.decode("utf-8"))


def km(a, b):
    if not a or not b:
        return None
    R = 6371.0
    dlat = math.radians(b[0] - a[0])
    dlng = math.radians(b[1] - a[1])
    h = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(a[0]))
         * math.cos(math.radians(b[0])) * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(h)) * 1000


def places(name, addr):
    body = json.dumps({"textQuery": name + " " + addr,
                       "languageCode": "ja", "regionCode": "JP",
                       "maxResultCount": 1}).encode("utf-8")
    r = run(["curl", "-fsSL", "--max-time", "30", "-X", "POST",
             "https://places.googleapis.com/v1/places:searchText",
             "-H", "Content-Type: application/json",
             "-H", "X-Goog-Api-Key: " + KEY,
             "-H", "X-Goog-FieldMask: "
                   "places.location,places.displayName,places.formattedAddress",
             "--data-binary", "@-"], data=body)
    ps = r.get("places") or []
    if not ps:
        return None
    return {"lat": ps[0]["location"]["latitude"],
            "lng": ps[0]["location"]["longitude"],
            "name": ps[0].get("displayName", {}).get("text", ""),
            "addr": ps[0].get("formattedAddress", "")}


def ggeo(addr):
    r = run(["curl", "-fsSL", "--max-time", "30",
             "https://maps.googleapis.com/maps/api/geocode/json?address="
             + urllib.parse.quote(addr) + "&language=ja&region=jp&key=" + KEY])
    if r.get("status") != "OK" or not r.get("results"):
        return None
    l = r["results"][0]["geometry"]["location"]
    return {"lat": l["lat"], "lng": l["lng"]}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・\-−―ー'\"]", "", s).lower()


def city_of(addr):
    a = unicodedata.normalize("NFKC", addr or "")
    a = re.sub(r"^日本[、,\s]*", "", a)
    a = re.sub(r"〒?\d{3}-?\d{4}\s*", "", a)
    m = re.search(r"(.{2,3}?[都道府県])(.+?[市区町村])", a)
    return m.group(2) if m else ""


def similar(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


s = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL).group(1))
print("対象: %d 件\n" % len(villas))

rows, geo, ok, ng = [], {}, 0, 0

for n, v in enumerate(villas, 1):
    vid = str(v["id"])
    name, addr = v.get("name", ""), (v.get("addr") or "").strip()
    ent = cache.get(vid)
    if ent is None:
        try:
            p = places(name, addr)
            time.sleep(0.2)
            g = ggeo(addr)
            time.sleep(0.15)
        except Exception as e:
            print("[%3d/%d] id=%-4s 取得失敗: %s" % (n, len(villas), vid, e))
            continue
        ent = {"p": p, "g": g}
        cache[vid] = ent
        save_cache()
    p, g = ent.get("p"), ent.get("g")

    warn = []
    if not p:
        warn.append("Places該当なし")
    else:
        sim = similar(name, p["name"])
        c_in, c_out = city_of(addr), city_of(p["addr"])
        if sim < 0.34:
            warn.append("名称ちがい")
        if c_in and c_out and c_in != c_out:
            warn.append("市区町村ちがい(%s→%s)" % (c_in, c_out))

    d_pg = km((p["lat"], p["lng"]), (g["lat"], g["lng"])) if (p and g) else None
    d_sp = None
    if v.get("geo") and p:
        d_sp = km((v["geo"]["lat"], v["geo"]["lng"]), (p["lat"], p["lng"]))
        if d_sp > 200:
            warn.append("保存座標と%.0fm相違" % d_sp)

    if p and not warn:
        geo[vid] = {"lat": round(p["lat"], 6), "lng": round(p["lng"], 6)}
        ok += 1
    else:
        ng += 1

    rows.append([vid, name, addr,
                 p["name"] if p else "", p["addr"] if p else "",
                 "%.0f" % d_pg if d_pg is not None else "",
                 "%.0f" % d_sp if d_sp is not None else "",
                 " / ".join(warn)])
    if n % 25 == 0:
        print("  %d 件処理 (採用 %d / 要確認 %d)" % (n, ok, ng))

io.open(os.path.join(OUT, "geo_places.json"), "w", encoding="utf-8").write(
    json.dumps(geo, ensure_ascii=False, indent=1))

with io.open(os.path.join(OUT, "geocheck.csv"), "w",
             encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "施設名", "入力した住所", "Placesが返した名称",
                "Placesが返した住所", "Places-Geocoding距離m",
                "保存座標との距離m", "警告"])
    w.writerows(rows)

print("\n採用 %d 件 / 要確認 %d 件" % (ok, ng))
print("  %s/geo_places.json  ← そのまま使える座標" % OUT)
print("  %s/geocheck.csv     ← 警告つきの行を目視で確認" % OUT)
