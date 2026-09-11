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
  python3 tools/blanks.py --ids 1,2,3   対象を明示（並行する波と重複させない）
  python3 tools/blanks.py --include-done  記録済みでも空欄が残る施設を出す
  python3 tools/blanks.py --yield        空欄数ではなく期待収量で並べる
  python3 tools/blanks.py --ikitai       サウナイキタイ未確認の施設に絞る
"""
import io, json, re, sys

CELL = r"(\w+):\s*\{\s*v:"          # 空白数を決め打ちしない


def ikitai_checked():
    """サウナイキタイを**体系的に走査し終えた**施設の id。

    サウナイキタイは温度・サウナ定員・水温・水深・休憩イス・ロウリュを
    **構造化して**持っており、公式がまず書かない項目がまとめて取れる。
    2026-09 に千葉61・山梨39・静岡43を走査して、掲載率6割前後で
    オーナー調査待ちだった項目が大きく動いた（`water_depth` 1→42 など）。

    **判定は data/ikitai-checked.json だけで行う。spec-data.js の出典URLで
    代用してはいけない。** 理由が2つある。

      1. **掲載が無かった施設に印が付かない。** 出典URLが残らないので
         「調べたが載っていなかった」と「まだ調べていない」を区別できず、
         同じ施設を何度も調べさせる（2026-09 に千葉36件・山梨23件が再掲された）。
      2. **単発で1項目だけ参照した施設が『走査済み』に見える。** 走査を始める前から
         出典URLを持つ施設が25あったが、うち7件は ikitai 出典が**1セルだけ**で
         5〜10項目が空いていた。出典URLで除外すると**この154項目が対象から消える。**
    """
    import json
    try:
        doc = json.load(io.open("data/ikitai-checked.json", encoding="utf-8"))
        return {str(v) for v in doc.get("checked", [])}
    except IOError:
        return set()


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
    have, nosrc = {}, {}
    for vid, blk in re.findall(r'^  "(\d+)": \{(.*?)\n  \},?', spec, re.M | re.S):
        have[vid] = set(re.findall(CELL, blk))
        # 出典URLの無い desk 値は初期一括投入のコホート。2026-08 の走査で
        # 566件すべてが at:'2026-07' と判明し、そこから誤りが複数出ている。
        # 施設を開くならついでに検証させる。
        nosrc[vid] = [k for k, body in re.findall(r"(\w+):\s*\{([^}]*)\}", blk)
                      if "src: 'desk'" in body and "url:" not in body]
    return villas, desk, opts, masters, have, nosrc


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
    villas, desk, opts, masters, have, nosrc = load()
    done = {m for line in io.open("data/desk-research.js", encoding="utf-8")
            for m in re.findall(r"id=(\d+)", line)}
    # 期待収量順。空欄の数ではなく「埋まる見込み」で並べる。
    # 項目ごとの現在の充足率を、その項目の机上での取りやすさの代理指標として使う。
    # 直近の波で分かったこと: 丁寧に調べても埋まるのは対象の空欄の2割で、
    # 残りは coldbath_season(4%) / stove(35%) / kitchen_type(42%) のような
    # 「公式が書かない項目」に集中している。空欄数で並べるとそこばかり当たる。
    yield_mode = "--yield" in sys.argv
    want = None
    if "--ids" in sys.argv:
        # 対象を明示する。並行して走っている波と重複させないため。
        # 指定した施設は done / 出典なし0 でも落とさない。
        want = set(sys.argv[sys.argv.index("--ids") + 1].split(","))
        done = done - want
    if "--include-done" in sys.argv:
        # 記録済みでも空欄が残っている施設を出す。波を重ねると、既に一度調べた
        # 施設に「その時は取れなかった項目」が残る。既定の done 除外はそれを
        # 隠してしまうので、後半の波ではこちらを使う。
        done = set()
    if "--ikitai" in sys.argv:
        # サウナイキタイで確認していない「サウナのある施設」に絞る。
        # sauna_exists が no / 未設定の施設は掲載がそもそも期待できない。
        checked = ikitai_checked()
        keep = set()
        for v in villas:
            vid = str(v["id"])
            if vid in checked:
                continue
            if "sauna" not in (v.get("tags") or []):
                continue          # yes / room のときだけタグが付く
            keep.add(vid)
        done = done | ({str(v["id"]) for v in villas} - keep)
    unsourced = "--unsourced" in sys.argv
    if unsourced:
        # 出典URLの無い desk 値の多い順。空欄ではなく検証対象を選ぶモード。
        rows = sorted(((len([k for k in nosrc.get(str(v["id"]), []) if k in desk]),
                        str(v["id"]), v) for v in villas), key=lambda r: -r[0])
    else:
        n_all = float(len(villas))
        fill = dict((k, sum(1 for v in villas
                            if k in have.get(str(v["id"]), set())) / n_all)
                    for k in desk)
        def score(v):
            miss = [k for k in desk if k not in have.get(str(v["id"]), set())]
            if yield_mode:
                # 充足率の合計 = その施設で埋まると期待できる項目数のめやす
                return sum(fill[k] for k in miss)
            return len(miss)
        rows = sorted(((score(v), str(v["id"]), v) for v in villas
                       if str(v["id"]) not in done), key=lambda r: -r[0])
    if want is not None:
        rows = [r for r in rows if r[1] in want]
    else:
        rows = [r for r in rows if r[0] > 0]
    rows = rows[:n]
    if "--prompt" not in sys.argv:
        print("desk項目 %d: %s" % (len(desk), " ".join(desk)))
        lbl = "出典なし" if unsourced else "空欄"
        print("上位%d件（%s合計 %d）" % (len(rows), lbl, sum(r[0] for r in rows)))
        for b, vid, v in rows:
            if isinstance(b, float):
                miss = [k for k in desk if k not in have.get(vid, set())]
                print("  id=%-4s 期待%.1f 空欄%-3d %s"
                      % (vid, b, len(miss), v["name"][:36]))
            else:
                print("  id=%-4s %s%-3d %s" % (vid, lbl, b, v["name"][:40]))
        return
    print("## 埋める項目と選択肢（spec.js の var O から生成。この値以外は使わない）\n")
    print(option_text(desk, opts, masters))
    print("\n## 調査対象（%d施設）\n" % len(rows))
    for b, vid, v in rows:
        miss = [k for k in desk if k not in have.get(vid, set())]
        # 広告クリック計測の中継URL（google.com/aclk）は単体で開いても施設に
        # 到達しない。2026-08 の ota 全件走査で14エントリ見つかっている。
        ikyu = (v.get("ota") or {}).get("ikyu") or ""
        if "google.com/aclk" in ikyu:
            ikyu = "(壊れたURL。一休で施設名を検索すること)"
        print("- id=%s 「%s」\n    住所: %s\n    公式: %s\n    一休: %s\n    空欄: %s"
              % (vid, v["name"], v.get("addr", ""), v.get("official") or "(なし)",
                 ikyu or "(なし)", ", ".join(miss)))
        ns = [k for k in nosrc.get(vid, []) if k in desk]
        if ns:
            print("    出典なし（ついでに検証）: %s" % ", ".join(ns))


main()
