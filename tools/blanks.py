#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机上調査の対象施設を選び、選択肢マスタつきの調査指示を出力する。

手で書いた正規表現と手で写した選択肢マスタで二度事故を起こしたので作った。

  1. spec-data.js のセル書式は `key:` のあとの空白数が揃っていない。
     `(\\w+): \\{ v:` のように空白1個を決め打ちすると大半を取りこぼし、
     調査済みの施設が「空欄10」に見える。実際 2026-08 にこれで14施設を
     二重調査させた。
  2. 選択肢マスタをプロンプトに手で写すと間違える。loyly を yes/no の
     2択と書いて auto を落としかけ、sauna_type に存在しない cabin を
     書いた。**マスタは spec.js の var O から生成する。**

  python3 tools/blanks.py            上位20施設を一覧
  python3 tools/blanks.py -n 14      件数を指定
  python3 tools/blanks.py --prompt   エージェントに渡す調査指示を出力
"""
import io, json, re, sys

CELL = r"(\w+):\s*\{\s*v:"          # 空白数を決め打ちしない


def load():
    spec = io.open("spec-data.js", encoding="utf-8").read()
    sjs = io.open("spec.js", encoding="utf-8").read()
    idx = io.open("index.html", encoding="utf-8").read()
    villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", idx, re.S).group(1))
    schema = re.findall(r"\{\s*k:\s*'(\w+)'([^}]*)\}", sjs)
    desk, opts = [], {}
    for k, rest in schema:
        if "ch: 'desk'" in rest.replace("ch:'desk'", "ch: 'desk'"):
            desk.append(k)
            mo = re.search(r"o:\s*'(\w+)'", rest)
            if mo:
                opts[k] = mo.group(1)
    masters = dict(re.findall(r"^\s*(\w+):\s*\{([^}]*)\},?\s*$", 
                              re.search(r"var O = \{(.*?)\n\s*\};", sjs, re.S).group(1), re.M))
    have = {vid: set(re.findall(CELL, blk))
            for vid, blk in re.findall(r'^  "(\d+)": \{(.*?)\n  \},?', spec, re.M | re.S)}
    return villas, desk, opts, masters, have


def option_text(desk, opts, masters):
    out = []
    for k in desk:
        o = opts.get(k)
        if not o or o not in masters:
            out.append("  %-14s 数値" % k)
            continue
        vals = re.findall(r"(\w+):\s*'([^']*)'", masters[o])
        out.append("  %-14s %s" % (k, " / ".join("%s（%s）" % v for v in vals)))
    return "\n".join(out)


def main():
    n = 20
    if "-n" in sys.argv:
        n = int(sys.argv[sys.argv.index("-n") + 1])
    villas, desk, opts, masters, have = load()
    done = {m for line in io.open("data/desk-research.js", encoding="utf-8")
            for m in re.findall(r"id=(\d+)", line)}
    rows = sorted(((len([k for k in desk if k not in have.get(str(v["id"]), set())]),
                    str(v["id"]), v) for v in villas if str(v["id"]) not in done),
                  key=lambda r: -r[0])
    rows = [r for r in rows if r[0] > 0][:n]
    if "--prompt" not in sys.argv:
        print("desk項目 %d: %s" % (len(desk), " ".join(desk)))
        print("未記録で空欄のある施設 上位%d件（空欄合計 %d）"
              % (len(rows), sum(r[0] for r in rows)))
        for b, vid, v in rows:
            print("  id=%-4s 空欄%-3d %s" % (vid, b, v["name"][:40]))
        return
    print("## 埋める項目と選択肢（spec.js の var O から生成。この値以外は使わない）\n")
    print(option_text(desk, opts, masters))
    print("\n## 調査対象（%d施設）\n" % len(rows))
    for b, vid, v in rows:
        miss = [k for k in desk if k not in have.get(vid, set())]
        print("- id=%s 「%s」\n    住所: %s\n    公式: %s\n    一休: %s\n    空欄: %s"
              % (vid, v["name"], v.get("addr", ""), v.get("official") or "(なし)",
                 (v.get("ota") or {}).get("ikyu") or "(なし)", ", ".join(miss)))


main()
