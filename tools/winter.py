#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""winter_access（冬季アクセス）を標高と県から導出する。チャネルA。

設計書はこの項目をチャネルAに置き「標高＋緯度＋県の道路規制情報から判定。
標高700m超＋日本海側は自動で『推奨』に倒す」としているが、実装されないまま
ch: 'owner' に分類され3件しか入っていなかった。標高は286件すべて揃っている
ので、ここで回収する。

**この項目だけは推定であり、他のチャネルA項目（標高・所要時間）のような
実測ではない。** 冬の運転に関わる情報なので、判定は警告側に倒す。

  判定ルール（rule v1）
    標高 >= 500m                    -> tire   スタッドレス・チェーン推奨
    標高 < 200m かつ太平洋沿岸の県   -> ok     通年問題なし
    200m <= 標高 < 500m             -> **記録しない**（下記）
    上記以外                         -> 記録しない

  **200〜500m は意図的に空けている。** この帯には伊豆高原（約250m）から
  那須（約450m）まで実態の異なる地域が混在し、標高だけでは判定できない。
  実際、手作業で入っていた3件はいずれもこの帯で、すべて tire だった。

    id=204 オーシャンビュー南熱海 290m / id=124 ドワーフの村 428m /
    id=210 熱海オーシャンハウス 439m

  標高だけの判定なら snow になるところを人間は tire と書いている。
  **推定が人間の判断より甘い側に出るなら、その帯は埋めるべきではない。**

  `closed`（冬季通行止めあり）も自動では絶対に付けない。
  実際の道路規制データが要るため、机上調査かオーナー回答に委ねる。

  閾値を設計書の700mではなく500mにしたのは、箱根仙石原（約650m）のように
  700m未満でも冬タイヤが要る地域が含まれるため。**過剰に警告する誤りは
  無害だが、警告し損ねる誤りは危険**という非対称性による。

  python3 tools/winter.py             判定結果の分布を出す（書き換えない）
  python3 tools/winter.py --write     spec-data.js に書き込む
"""
import io, json, re, sys

# 冬季に積雪がまず無い低地を持つ県。標高200m未満のときだけ ok に倒す。
COASTAL = ("千葉県", "茨城県", "神奈川県", "静岡県", "埼玉県", "東京都")

TIRE_M = 500
SNOW_M = 200
AT = "2026-09"


def judge(pref, ele):
    if ele is None:
        return None, "標高なし"
    if ele >= TIRE_M:
        return "tire", "標高%dm >= %dm" % (ele, TIRE_M)
    if ele >= SNOW_M:
        return None, "標高%d〜%dm は判定を保留する帯" % (SNOW_M, TIRE_M)
    if pref in COASTAL:
        return "ok", "標高%dm・%sの低地" % (ele, pref)
    return None, "%s は太平洋沿岸の県に含まれない" % pref


def main():
    spec = io.open("spec-data.js", encoding="utf-8").read()
    idx = io.open("index.html", encoding="utf-8").read()
    villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", idx, re.S).group(1))
    pref = {}
    for v in villas:
        m = re.match(r"(.+?[都道府県])", v.get("addr") or "")
        pref[str(v["id"])] = (m.group(1) if m else "?", v["name"])

    rows, counts, skip = [], {}, {}
    for vid, blk in re.findall(r'^  "(\d+)": \{(.*?)\n  \},?', spec, re.M | re.S):
        cur = re.search(r"winter_access:\s*\{([^}]*)\}", blk)
        me = re.search(r"elevation:\s*\{\s*v:\s*([-\d.]+)", blk)
        p, name = pref.get(vid, ("?", "?"))
        val, why = judge(p, float(me.group(1)) if me else None)
        if val is None:
            skip[why] = skip.get(why, 0) + 1
            continue
        if cur:
            old = re.search(r"v:\s*'(\w+)'", cur.group(1)).group(1)
            if old != val:
                print("  [!] id=%-4s 既存 %s -> 判定 %s  %s  %s"
                      % (vid, old, val, why, name[:24]))
            counts["（既存あり）"] = counts.get("（既存あり）", 0) + 1
            continue
        counts[val] = counts.get(val, 0) + 1
        rows.append((vid, val, why))

    print("\n判定結果（rule v1: tire>=%dm / ok=沿岸の標高%dm未満）" % (TIRE_M, SNOW_M))
    for k in ("tire", "snow", "ok", "（既存あり）"):
        if k in counts:
            print("  %-10s %3d 件" % (k, counts[k]))
    for k, n in skip.items():
        print("  %-10s %3d 件（記録しない）" % (k, n))
    print("  closed      0 件（自動では付けない）")
    print("\n書き込み対象 %d 件" % len(rows))

    if "--write" not in sys.argv:
        print("（--write を付けると spec-data.js に書き込みます）")
        return

    for vid, val, why in rows:
        m = re.search(r'(^  "%s": \{.*?)(\n  \},?)' % vid, spec, re.M | re.S)
        blk, tail = m.group(1), m.group(2)
        cell = "\n    winter_access: { v: '%s', src: 'auto', at: '%s' }" % (val, AT)
        spec = spec.replace(m.group(0), blk.rstrip().rstrip(",") + "," + cell + tail, 1)
    io.open("spec-data.js", "w", encoding="utf-8").write(spec)
    print("spec-data.js を更新しました（%d 件）" % len(rows))


main()
