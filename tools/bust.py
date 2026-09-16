# -*- coding: utf-8 -*-
"""共有アセットの参照に内容ハッシュを付ける（キャッシュ対策）。

`spec.js` / `spec.css` / `reviews.js` / `reviews.css` / `spec-data.js` は
index.html と villas/*.html から `<script src>` / `<link href>` で読まれる。
**素の URL のままだと、更新してもブラウザが古い版を使い続ける。**
GitHub Pages でも同じで、再訪者に古い CSS/JS が配られる。
実際に「直したのに反映されない」を開発中に何度も起こした。

    python3 tools/bust.py            現在の差分を表示
    python3 tools/bust.py --write    書き込む

**これらのファイルを編集したら必ず実行すること。**
"""
import glob, hashlib, io, os, re, sys

ASSETS = ["spec.js", "spec.css", "reviews.js", "reviews.css", "spec-data.js",
          "villa.js", "data/villas-lite.js"]


def short(path):
    h = hashlib.sha256(io.open(path, "rb").read()).hexdigest()
    return h[:8]


def main():
    write = "--write" in sys.argv
    ver = {}
    for a in ASSETS:
        if os.path.exists(a):
            ver[a] = short(a)
    files = ["index.html"] + sorted(glob.glob("villas/*.html"))
    changed = 0
    for f in files:
        s = io.open(f, encoding="utf-8").read()
        orig = s
        for a, v in ver.items():
            # ../spec.js もしくは spec.js（既存の ?v= は付け替える）
            s = re.sub(r'((?:src|href)=")((?:\.\./)?' + re.escape(a) + r')(?:\?v=[0-9a-f]+)?(")',
                       lambda m: m.group(1) + m.group(2) + "?v=" + v + m.group(3), s)
        if s != orig:
            changed += 1
            if write:
                io.open(f, "w", encoding="utf-8").write(s)
    for a, v in sorted(ver.items()):
        print("  %-14s %s" % (a, v))
    print("%s %d / %d ファイル" % ("更新した" if write else "更新が要る", changed, len(files)))
    if not write and changed:
        print("→ python3 tools/bust.py --write")


main()
