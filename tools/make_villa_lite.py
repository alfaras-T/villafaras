# -*- coding: utf-8 -*-
"""data/villas-lite.js を作る（個別ページ用の軽量データ）。

**個別ページは index.html の VILLAS（234KB）を読み込めない。** だが
「似たサウナのヴィラ」やパンくずには施設名・スラッグ・県・タグ・価格が要る。
286ページの HTML に書き込むとデータとUIが癒着するので、1本の JS に出す。

    python3 tools/make_villa_lite.py

index.html の VILLAS / VILLA_SLUGS を編集したら実行し、tools/bust.py も流すこと。
"""
import io, json, os, re

src = io.open("index.html", encoding="utf-8").read()

i = src.index("const VILLAS=") + len("const VILLAS=")
villas = json.loads(src[i:src.index("];", i) + 1])

m = re.search(r"VILLA_SLUGS=\{(.*?)\};", src, re.S)
slugs = {}
for k, v in re.findall(r'(\d+):"([^"]*)"', m.group(1)):
    slugs[int(k)] = v

out = []
for v in villas:
    out.append({
        "i": v["id"],
        "n": v["name"],
        "s": slugs.get(v["id"], ""),
        "p": v["pref"],
        "t": v.get("tags") or [],
        "y": v.get("pnum") or 0,        # 一棟あたりの目安（index の絞り込みと同じ軸）
        "pp": v.get("pricePerPerson") or "",
        "c": v.get("capacity") or "",
    })

body = ("/* 自動生成: python3 tools/make_villa_lite.py\n"
        "   個別ページ用の軽量データ。編集しないこと。 */\n"
        "window.VILLAFARAS_LITE = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")

if not os.path.isdir("data"):
    os.makedirs("data")
io.open("data/villas-lite.js", "w", encoding="utf-8").write(body)
print("data/villas-lite.js  %d件 / %.1fKB" % (len(out), len(body.encode("utf-8")) / 1024.0))
missing = [v["i"] for v in out if not v["s"]]
if missing:
    print("!! スラッグが無い id:", missing)
