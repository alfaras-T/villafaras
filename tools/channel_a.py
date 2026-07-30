#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
villafaras チャネルA 自動導出
================================================================================
座標から機械的に算出できる項目を、286件すべてについて取得する。
オーナーへの依頼は一切発生しない。

  1. 住所 → 座標          国土地理院 AddressSearch
  2. 座標 → 標高          国土地理院 getelevation
  3. 周辺施設の候補抽出    Overpass API (OpenStreetMap)
  4. 車での所要時間        OSRM table service
                          ※直線距離ではなく実走行時間。山間部で2〜3倍ずれるため。

実行:
    python3 channel_a.py --repo /path/to/villafaras

  ・中断しても cache/ に保存されるので、再実行すれば続きから走る
  ・出力は spec-data-auto.js（断片）と review.csv（要目視確認の一覧）
  ・リポジトリのファイルは書き換えない。マージは目視確認のあとに行う

依存: 標準ライブラリのみ
================================================================================
"""

import argparse
import csv
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "villafaras-channelA/1.0 (+https://villafaras.jp)"

# --- 各APIへの間隔（秒）。公共APIなので必ず礼儀正しく叩く --------------------
WAIT_GSI      = 0.5
WAIT_ELEV     = 0.4
WAIT_OVERPASS = 3.0
WAIT_OSRM     = 1.2

# --- 検索半径（m）------------------------------------------------------------
RADIUS = {
    "supermarket": 20000,
    "conveni":     15000,
    "ic":          40000,
    "station":     25000,
    "onsen":       25000,
}

# Overpass のタグ条件
OVERPASS_TAGS = {
    "supermarket": '["shop"="supermarket"]',
    "conveni":     '["shop"="convenience"]',
    "ic":          '["highway"="motorway_junction"]',
    "station":     '["railway"="station"]',
    "onsen":       '["amenity"="public_bath"]',
}

# 名前も表示すると有用な項目（それ以外は分数のみ）
WITH_NAME = ("ic", "station")


# ==============================================================================
# 汎用
# ==============================================================================

def http_json(url, data=None, timeout=90, retries=3):
    """JSONを取得。一時的な失敗はリトライする。"""
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data,
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            # 429/5xx はサーバ側の都合。待って引き下がる
            time.sleep(3 * (attempt + 1))
    raise last


def haversine_km(a, b):
    R = 6371.0
    dlat = math.radians(b[0] - a[0])
    dlng = math.radians(b[1] - a[1])
    h = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(h))


class Cache(object):
    """中断・再開のための単純なJSONキャッシュ。"""

    def __init__(self, path):
        self.path = path
        self.data = {}
        if os.path.exists(path):
            try:
                self.data = json.load(io.open(path, encoding="utf-8"))
            except Exception:
                self.data = {}

    def get(self, key):
        return self.data.get(str(key))

    def put(self, key, value):
        self.data[str(key)] = value
        self.flush()

    def flush(self):
        tmp = self.path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data, ensure_ascii=False, indent=1))
        os.replace(tmp, self.path)


# ==============================================================================
# 1. 入力（リポジトリの index.html から VILLAS を取り出す）
# ==============================================================================

def load_villas(repo):
    path = os.path.join(repo, "index.html")
    s = io.open(path, encoding="utf-8").read()
    m = re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL)
    if not m:
        raise SystemExit("index.html から VILLAS 配列を取り出せませんでした")
    villas = json.loads(m.group(1))
    print("読み込み: %d 件" % len(villas))
    return villas


# ==============================================================================
# 2. ジオコーディング（国土地理院）
# ==============================================================================

def geocode(addr):
    """
    国土地理院 AddressSearch。
    戻り値 GeoJSON の coordinates は [経度, 緯度] の順であることに注意。
    """
    url = ("https://msearch.gsi.go.jp/address-search/AddressSearch?q="
           + urllib.parse.quote(addr))
    res = http_json(url)
    if not res:
        return None
    best = res[0]
    lng, lat = best["geometry"]["coordinates"]
    return {
        "lat": lat,
        "lng": lng,
        "matched": best.get("properties", {}).get("title", ""),
        "hits": len(res),
    }


def geocode_confidence(addr, got):
    """
    粗いマッチ（市町村レベルで止まっている等）を検出する。
    ここで拾ったものは review.csv に回し、人が目視で確認する。
    自動判定を鵜呑みにして誤った座標を掲載しないための関門。
    """
    if not got:
        return "NG_ジオコーディング失敗"
    # index.html に元から入っていた座標は検証済みとみなす
    if got.get("source") == "existing":
        return ""
    title = got.get("matched") or ""
    warn = []
    # 番地の数字が結果に反映されていない = 大字どまりの可能性
    if re.search(r"\d", addr) and not re.search(r"\d", title):
        warn.append("番地未反映")
    if len(title) < 8:
        warn.append("マッチが粗い")
    if got.get("hits", 0) > 12:
        warn.append("候補過多")
    return ",".join(warn)


# ==============================================================================
# 3. 標高（国土地理院）
# ==============================================================================

def elevation(lat, lng):
    url = ("https://cyberjapandata2.gsi.go.jp/general/dem/scripts/"
           "getelevation.php?lon=%s&lat=%s&outtype=JSON" % (lng, lat))
    res = http_json(url, timeout=40)
    v = res.get("elevation")
    if v in (None, "-----", ""):
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


# ==============================================================================
# 4. 周辺施設の候補（Overpass / OpenStreetMap）
# ==============================================================================

def overpass_candidates(lat, lng):
    """
    5カテゴリぶんを1リクエストにまとめる。
    施設ごとに5回叩くと286×5=1430リクエストになり、公共サーバに対して失礼。
    """
    parts = []
    for key, tag in OVERPASS_TAGS.items():
        parts.append('nwr%s(around:%d,%.6f,%.6f);'
                     % (tag, RADIUS[key], lat, lng))
    q = "[out:json][timeout:120];(%s);out center tags;" % "".join(parts)
    data = urllib.parse.urlencode({"data": q}).encode("utf-8")
    res = http_json("https://overpass-api.de/api/interpreter",
                    data=data, timeout=180)

    out = dict((k, []) for k in OVERPASS_TAGS)
    for el in res.get("elements", []):
        tags = el.get("tags", {})
        c = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
        if c.get("lat") is None or c.get("lon") is None:
            continue
        p = (c["lat"], c["lon"])
        name = tags.get("name") or tags.get("name:ja") or ""

        if tags.get("shop") == "supermarket":
            k = "supermarket"
        elif tags.get("shop") == "convenience":
            k = "conveni"
        elif tags.get("highway") == "motorway_junction":
            k = "ic"
        elif tags.get("railway") == "station":
            k = "station"
        elif tags.get("amenity") == "public_bath":
            k = "onsen"
        else:
            continue

        out[k].append({
            "name": name,
            "lat": p[0],
            "lng": p[1],
            "km": round(haversine_km((lat, lng), p), 2),
        })

    # 直線距離で上位3件に絞る。
    # 直線最短が走行最短とは限らないため、1件ではなく3件をルート計算に回す。
    for k in out:
        out[k] = sorted(out[k], key=lambda x: x["km"])[:3]
    return out


# ==============================================================================
# 5. 車での所要時間（OSRM table service）
# ==============================================================================

def driving_minutes(origin, candidates):
    """
    origin から各候補への所要時間をまとめて1リクエストで取得する。
    table service は sources=0 で「起点→全destination」を返す。
    """
    if not candidates:
        return None
    coords = ["%.6f,%.6f" % (origin[1], origin[0])]
    for c in candidates:
        coords.append("%.6f,%.6f" % (c["lng"], c["lat"]))
    url = ("https://router.project-osrm.org/table/v1/driving/"
           + ";".join(coords) + "?sources=0&annotations=duration")
    res = http_json(url, timeout=90)
    if res.get("code") != "Ok":
        return None
    row = res.get("durations", [[]])[0]
    best = None
    for i, c in enumerate(candidates):
        sec = row[i + 1] if i + 1 < len(row) else None
        if sec is None:
            continue
        mins = int(round(sec / 60.0))
        if best is None or mins < best["min"]:
            best = {"min": mins, "name": c["name"], "km": c["km"]}
    return best


# ==============================================================================
# 6. spec-data.js 形式への出力
# ==============================================================================

def js_escape(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def build_js(results, at):
    """
    spec-data.js に貼り付けられる断片を組み立てる。
    src は 'auto'（座標から算出）。at は算出年月。
    """
    lines = []
    lines.append("/* ------------------------------------------------------------------")
    lines.append("   チャネルA 自動導出分（%s 時点）" % at)
    lines.append("   標高: 国土地理院 / 周辺施設: OpenStreetMap contributors (ODbL)")
    lines.append("   所要時間: OSRM による車のルート計算（直線距離ではない）")
    lines.append("   ------------------------------------------------------------------ */")

    for vid in sorted(results, key=lambda x: int(x)):
        r = results[vid]
        f = r.get("fields") or {}
        if not f:
            continue
        rows = []
        for k in ("elevation", "supermarket", "conveni", "ic", "station", "onsen"):
            if f.get(k) is None:
                continue
            v = f[k]
            if isinstance(v, str):
                rows.append("    %-12s { v: '%s', src: 'auto', at: '%s' }"
                            % (k + ":", js_escape(v), at))
            else:
                rows.append("    %-12s { v: %s, src: 'auto', at: '%s' }"
                            % (k + ":", v, at))
        if not rows:
            continue
        lines.append("")
        lines.append("  \"%s\": {  /* %s */" % (vid, r.get("name", "")))
        lines.append(",\n".join(rows))
        lines.append("  },")
    return "\n".join(lines) + "\n"


# ==============================================================================
# メイン
# ==============================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="villafaras リポジトリのパス")
    ap.add_argument("--out", default="out", help="出力先ディレクトリ")
    ap.add_argument("--limit", type=int, default=0, help="先頭N件だけ処理（動作確認用）")
    ap.add_argument("--only-geocode", action="store_true",
                    help="座標取得だけ行い、周辺検索は行わない")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cache_dir = os.path.join(args.out, "cache")
    os.makedirs(cache_dir, exist_ok=True)

    c_geo  = Cache(os.path.join(cache_dir, "geo.json"))
    c_elev = Cache(os.path.join(cache_dir, "elev.json"))
    c_near = Cache(os.path.join(cache_dir, "near.json"))
    c_time = Cache(os.path.join(cache_dir, "time.json"))

    villas = load_villas(args.repo)
    if args.limit:
        villas = villas[:args.limit]

    at = time.strftime("%Y-%m")
    results = {}
    review = []

    for n, v in enumerate(villas, 1):
        vid = str(v["id"])
        name = v.get("name", "")
        addr = (v.get("addr") or "").strip()
        print("[%3d/%d] id=%-4s %s" % (n, len(villas), vid, name[:34]))

        # --- 座標 ---------------------------------------------------------
        # index.html に既に geo があるものは信用して再取得しない
        if v.get("geo"):
            geo = {"lat": v["geo"]["lat"], "lng": v["geo"]["lng"],
                   "matched": "(既存データ)", "hits": 1, "source": "existing"}
        else:
            geo = c_geo.get(vid)
            if geo is None:
                try:
                    geo = geocode(addr)
                except Exception as e:
                    print("      ジオコーディング失敗: %s" % e)
                    geo = None
                if geo:
                    geo["source"] = "gsi"
                c_geo.put(vid, geo or {})
                time.sleep(WAIT_GSI)
            if not geo:
                geo = None

        warn = geocode_confidence(addr, geo)
        if warn:
            review.append([vid, name, addr,
                           (geo or {}).get("matched", ""),
                           (geo or {}).get("lat", ""), (geo or {}).get("lng", ""),
                           warn])
        if not geo:
            continue

        lat, lng = geo["lat"], geo["lng"]
        fields = {}

        if not args.only_geocode:
            # --- 標高 -----------------------------------------------------
            e = c_elev.get(vid)
            if e is None:
                try:
                    e = {"m": elevation(lat, lng)}
                except Exception as ex:
                    print("      標高取得失敗: %s" % ex)
                    e = {"m": None}
                c_elev.put(vid, e)
                time.sleep(WAIT_ELEV)
            if e.get("m") is not None:
                fields["elevation"] = e["m"]

            # --- 周辺施設の候補 -------------------------------------------
            near = c_near.get(vid)
            if near is None:
                try:
                    near = overpass_candidates(lat, lng)
                except Exception as ex:
                    print("      Overpass失敗: %s" % ex)
                    near = None
                c_near.put(vid, near or {})
                time.sleep(WAIT_OVERPASS)
            near = near or {}

            # --- 所要時間 -------------------------------------------------
            tm = c_time.get(vid)
            if tm is None:
                tm = {}
                for k in ("supermarket", "conveni", "ic", "station", "onsen"):
                    cands = near.get(k) or []
                    if not cands:
                        tm[k] = None
                        continue
                    try:
                        tm[k] = driving_minutes((lat, lng), cands)
                    except Exception as ex:
                        print("      OSRM失敗(%s): %s" % (k, ex))
                        tm[k] = None
                    time.sleep(WAIT_OSRM)
                c_time.put(vid, tm)

            for k, best in (tm or {}).items():
                if not best:
                    continue
                if k in WITH_NAME and best.get("name"):
                    fields[k] = "%s %d分" % (best["name"], best["min"])
                else:
                    fields[k] = best["min"]

        results[vid] = {"name": name, "geo": geo, "fields": fields}

    # --- 出力 -------------------------------------------------------------
    js_path = os.path.join(args.out, "spec-data-auto.js")
    io.open(js_path, "w", encoding="utf-8").write(build_js(results, at))

    geo_path = os.path.join(args.out, "geo.json")
    io.open(geo_path, "w", encoding="utf-8").write(json.dumps(
        dict((k, {"lat": r["geo"]["lat"], "lng": r["geo"]["lng"]})
             for k, r in results.items() if r.get("geo")),
        ensure_ascii=False, indent=1))

    rv_path = os.path.join(args.out, "review.csv")
    with io.open(rv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "施設名", "入力した住所", "マッチした住所",
                    "緯度", "経度", "警告"])
        w.writerows(review)

    got = sum(1 for r in results.values() if r.get("fields"))
    print("")
    print("完了: 座標 %d 件 / 項目取得 %d 件 / 要確認 %d 件"
          % (len(results), got, len(review)))
    print("  %s" % js_path)
    print("  %s" % geo_path)
    print("  %s  ← 先にこれを確認する" % rv_path)



# ============================== CURL_FALLBACK_PATCH ==========================
import subprocess as _sp
_TRANSPORT = {}

def _urllib_json(url, data, timeout):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def _curl_json(url, data, timeout):
    cmd = ["curl", "-fsSL", "--max-time", str(int(timeout)),
           "-H", "User-Agent: " + UA]
    if data is not None:
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded",
                "--data-binary", "@-"]
    cmd += [url]
    p = _sp.run(cmd, input=data, stdout=_sp.PIPE, stderr=_sp.PIPE)
    if p.returncode != 0:
        raise IOError("curl exit %d: %s"
                      % (p.returncode, p.stderr.decode("utf-8", "replace")[:200]))
    return json.loads(p.stdout.decode("utf-8"))

def http_json(url, data=None, timeout=90, retries=3):
    host = urllib.parse.urlparse(url).netloc
    order = ([_TRANSPORT[host]] if host in _TRANSPORT else [_urllib_json, _curl_json])
    last = None
    for attempt in range(retries):
        for fetch in order:
            try:
                res = fetch(url, data, timeout)
                if host not in _TRANSPORT:
                    _TRANSPORT[host] = fetch
                    if fetch is _curl_json:
                        print("      （%s は curl 経由に切り替えました）" % host)
                return res
            except Exception as e:
                last = e
        time.sleep(3 * (attempt + 1))
    raise last
# ============================================================================


if __name__ == "__main__":
    main()
