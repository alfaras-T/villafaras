#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spec-survey.html 用の軽い施設一覧を index.html から作る。

調査票はオーナーがメールのリンクから開く。**index.html は434KBあり、
施設名と住所を出すためだけに読ませるのは重い。** id / name / addr だけを
切り出した 20KB 弱のファイルを配る。

  python3 tools/make_survey_villas.py   ->  data/survey-villas.js
"""
import io, json, re

idx = io.open("index.html", encoding="utf-8").read()
m = re.search(r"const VILLAS=(\[.*?\]);", idx, re.S)
if not m:
    raise SystemExit("!! index.html の VILLAS を読めません")
villas = json.loads(m.group(1))

rows = []
for v in villas:
    rows.append('  %s: {n: %s, a: %s}' % (
        json.dumps(str(v["id"])),
        json.dumps(v.get("name", ""), ensure_ascii=False),
        json.dumps(v.get("addr", ""), ensure_ascii=False)))

out = (u"/* 自動生成 — tools/make_survey_villas.py。直接編集しない。\n"
       u"   spec-survey.html が施設の同定に使う最小の一覧。 */\n"
       u"window.VILLAFARAS_SURVEY_VILLAS = {\n" + u",\n".join(rows) + u"\n};\n")
io.open("data/survey-villas.js", "w", encoding="utf-8").write(out)
print("data/survey-villas.js を書きました（%d 施設 / %d バイト）"
      % (len(villas), len(out.encode("utf-8"))))
