#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, json, re, sys

AUTO = "out/spec-data-auto.js"
DATA = "spec-data.js"
SPEC = "spec.js"

cur = io.open(DATA, encoding="utf-8").read()
body = cur[cur.index("window.VILLAFARAS_SPEC = {"):]
body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)

def parse(text):
    out = {}
    for vid, blk in re.findall(r'"(\d+)":\s*\{(.*?)\n\s*\}', text, re.DOTALL):
        fields = {}
        for k, v in re.findall(r"(\w+):\s*(\{[^}]*\})", blk):
            fields[k] = " ".join(v.split())
        if fields:
            out[vid] = fields
    return out

existing = parse(body)
auto = parse(io.open(AUTO, encoding="utf-8").read())
print("既存の手入力: %d 件 / 自動導出: %d 件" % (len(existing), len(auto)))

AUTO_KEYS = ("elevation", "supermarket", "conveni", "ic", "station", "onsen")
merged, added = {}, 0
for vid in set(list(existing) + list(auto)):
    f = dict(existing.get(vid, {}))
    for k, v in (auto.get(vid) or {}).items():
        if k in AUTO_KEYS and k not in f:
            f[k] = v
            added += 1
    merged[vid] = f
print("統合後: %d 件 / 追加フィールド %d 個" % (len(merged), added))

html = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", html, re.DOTALL).group(1))
names = dict((str(v["id"]), v.get("name", "")) for v in villas)

ORDER = ["stove", "sauna_type", "sauna_temp", "sauna_cap", "loyly", "heat_time",
         "sauna_hours", "coldbath", "chiller", "water_temp", "water_src",
         "water_depth", "outdoor_rest", "rest_chair"] + list(AUTO_KEYS)

def key_order(k):
    return (ORDER.index(k), k) if k in ORDER else (len(ORDER), k)

out = ["""/* ==========================================================================
   villafaras 施設スペック データ
   --------------------------------------------------------------------------
   spec.js より先に読み込むこと。
   形式: VILLAFARAS_SPEC[villaId] = { fieldKey: { v: 値, src: 出典, at: 調査日, url: 出典URL } }

     src : 'owner'（施設回答） / 'desk'（公式サイト調べ） / 'auto'（座標算出） / 'review'（宿泊者）
     at  : 'YYYY-MM' 形式の調査日
     url : src が 'desk' の場合は出典URLを必ず記録する

   アクセス系（標高・最寄り各所）はチャネルAで自動導出したもの。
   座標は Google Places（施設名+住所）で取得し、既知の32件と照合して検証済み。
   周辺施設: OpenStreetMap contributors (ODbL) / 標高: 国土地理院
   所要時間: OSRM による車のルート計算（直線距離ではない）
   ========================================================================== */
window.VILLAFARAS_SPEC = {"""]

for vid in sorted(merged, key=lambda x: int(x)):
    f = merged[vid]
    if not f:
        continue
    keys = sorted(f, key=key_order)
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
print("%s を更新しました" % DATA)

s = io.open(SPEC, encoding="utf-8").read()
n = 0
for a, b in (("{ k: 'ic',            l: '最寄りIC',       u: '分',  ch: 'auto' },",
              "{ k: 'ic',            l: '最寄りIC',                 ch: 'auto' },"),
             ("{ k: 'station',       l: '最寄り駅',       u: '分',  ch: 'auto' },",
              "{ k: 'station',       l: '最寄り駅',                 ch: 'auto' },")):
    if a in s:
        s = s.replace(a, b, 1)
        n += 1
print("spec.js: 単位の重複を %d 箇所修正" % n)

OLD = ("'「未調査」は情報が未確認であることを示すもので、"
       "設備が存在しないことを意味しません。' +")
NEW = ("'「未調査」は情報が未確認であることを示すもので、"
       "設備が存在しないことを意味しません。<br>' +\n"
       "        '周辺情報: © OpenStreetMap contributors ／ 標高: 国土地理院 ／ "
       "所要時間は車での目安' +")
if OLD in s and "OpenStreetMap" not in s:
    s = s.replace(OLD, NEW, 1)
    print("spec.js: 出典表記を追加")
elif "OpenStreetMap" in s:
    print("spec.js: 出典表記は追加済み")
else:
    print("spec.js: !! フッタの差し込み位置が見つかりません")
io.open(SPEC, "w", encoding="utf-8").write(s)
