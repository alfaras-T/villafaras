#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, json, re, sys

SRCS = sys.argv[1:] or ["out/spec-data-desk.js"]
DATA = "spec-data.js"

def parse(text):
    """施設ブロックを**波括弧の対応**で切り出す。

    **終端を `\\n\\s*\\}` で探してはいけない。** 2026-09 に候補ファイルを

        "0":  { stove:{...},
                rest_chair:{...} },

    と**閉じ括弧を最終セルと同じ行**に書いたところ、この終端が見つからず
    id=0 のブロックが**ファイル全体を飲み込んだ**。結果、23施設ぶんのセルが
    すべて id=0 に集まり、同名フィールドは後勝ちで潰れて、
    **id=53 の sauna_temp と id=56 の stove が id=0 に書き込まれた。**
    エラーも警告も出ず「追加 6 フィールド」とだけ表示された
    （23施設70セルのはずだった）。

    件数を見ていなければ気づけなかった。**入力の書式に依存しない読み方にする。**
    """
    out = {}
    for m in re.finditer(r'"(\d+)":\s*\{', text):
        vid = m.group(1)
        i = text.index("{", m.start())
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = text[i + 1:j]
        # ブロックの中に別の施設idが現れたら、切り出しが破綻している。
        if re.search(r'"\d+":\s*\{', blk):
            raise SystemExit(
                "!! id=%s のブロックに別の施設idが入っています。"
                "候補ファイルの波括弧の対応を確認してください。" % vid)
        f = {}
        for k, v in re.findall(r"(\w+):\s*(\{[^}]*\})", blk):
            f[k] = " ".join(v.split())
        if f:
            out[vid] = f
    return out

# spec.js の SCHEMA に無い項目は入れない。
# **廃止した項目が一次記録に残っていると、マージで黙って復活する。**
# 2026-09 に early_late を early_checkin / late_checkout へ分割して
# spec-data.js から消したが、data/desk-research.js には古い early_late の
# 記録が残っており、次のマージで15施設ぶんが復活した（validate.py が
# 「SCHEMA にない項目」15件で検出）。スキーマを正として弾く。
SCHEMA_KEYS = set(re.findall(r"k:\s*'(\w+)'",
                             io.open("spec.js", encoding="utf-8").read()))

cur = io.open(DATA, encoding="utf-8").read()
head = cur[:cur.index("window.VILLAFARAS_SPEC = {")]
existing = parse(re.sub(r"/\*.*?\*/", "", cur, flags=re.DOTALL))
desk = {}
for src in SRCS:
    for vid, f in parse(io.open(src, encoding="utf-8").read()).items():
        desk.setdefault(vid, {}).update(f)
print("読み込み: %s" % ", ".join(SRCS))

merged, added, skipped = {}, 0, 0
dropped = {}
for vid in set(list(existing) + list(desk)):
    f = dict(existing.get(vid, {}))
    for k, v in (desk.get(vid) or {}).items():
        if k not in SCHEMA_KEYS and k not in f:
            dropped.setdefault(k, []).append(vid)
            continue
        if k in f:
            skipped += 1
        else:
            f[k] = v
            added += 1
    merged[vid] = f
print("追加 %d フィールド / 既存を優先して見送り %d" % (added, skipped))
if dropped:
    print("!! spec.js の SCHEMA に無いため入れなかった項目:")
    for k in sorted(dropped):
        ids = dropped[k]
        print("     %-16s %d 施設（id=%s%s）"
              % (k, len(ids), ", ".join(sorted(ids, key=int)[:8]),
                 " ほか" if len(ids) > 8 else ""))

html = io.open("index.html", encoding="utf-8").read()
villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", html, re.DOTALL).group(1))
names = dict((str(v["id"]), v.get("name", "")) for v in villas)

ORDER = ["sauna_exists", "sauna_type", "stove", "sauna_temp", "sauna_cap", "loyly",
         "heat_time", "sauna_hours", "coldbath", "chiller", "water_temp", "water_src",
         "water_depth", "outdoor_rest", "rest_chair", "villa_type", "neighbor_dist",
         "kitchen_type", "kitchen_burners", "bbq_roof", "firepit",
         "capacity", "comfort_cap", "pet_ok", "steps", "wifi",
         "elevation", "supermarket", "conveni", "ic", "station", "onsen"]
def ko(k):
    return (ORDER.index(k), k) if k in ORDER else (len(ORDER), k)

out = [head + "window.VILLAFARAS_SPEC = {"]
for vid in sorted(merged, key=lambda x: int(x)):
    f = merged[vid]
    if not f:
        continue
    keys = sorted(f, key=ko)
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
print("%s を更新しました（%d 施設）" % (DATA, len(merged)))
