# -*- coding: utf-8 -*-
"""紹介文（feature / desc）の人数と capacity の食い違いを洗い出す。

DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**
ことがほとんど（CLAUDE.md 参照）。capacity に出典URLが付いている施設なら、
食い違いは紹介文の側の誤りと確定できる。利用者に見える誤りなので直す価値がある。

  python3 tools/prose_cap.py          該当施設と、人数を含む文を出す
  python3 tools/prose_cap.py --all    出典なしの施設も出す
"""
import io
import re
import json
import sys

NUM = r'(?:最大|定員)\s*([0-9０-９]+)\s*(?:名|人)'


def zen(s):
    return s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))


# 人数が「施設全体の定員」以外を指している合図。**数字の近くにある場合だけ**数える。
# 文のどこかにあるだけでは駄目で、それだと
# 「檜のサウナや露天の星空ジャグジーも備え、最大14名まで宿泊できます」（id=13）を
# サウナ定員と誤判定する。実際にはこの14は施設の定員で、紹介文の側の誤り。
#
#   サウナ定員   「最大3名まで入れる専用サウナ」（id=41）        … 直後
#   浴場の定員   「温泉大浴場は最大4名同時入浴可能」（id=137）    … 直前
#   棟別の定員   「A棟は最大14名まで収容できる」（id=117）       … 直前
#   日帰りの人数 「日帰り利用なら最大20名まで」（id=25）          … 直前
#   プランの別   「半棟貸切（最大7名）」（id=51）                 … 直前
#   料金の区切り 「最大5名同一料金。」（id=126）                  … 直後
BEFORE = 10   # 数字の前をどこまで見るか（文字数）
AFTER = 18    # 数字の後をどこまで見るか（「最大8人まで入れる国産檜のオーバルサウナ」が入る長さ）
OTHER = ["サウナ", "大浴場", "入浴", "プール", "日帰り", "半棟", "同一料金",
         "母屋", "大型棟", "A棟", "B棟", "貸切（", "室のみ"]


def other_subject(sent, num):
    """人数が施設全体の定員以外を指している疑いがあるか。数字の近傍だけ見る。"""
    hit = []
    for m in re.finditer(NUM, sent):
        if zen(m.group(1)) != num:
            continue
        near = sent[max(0, m.start() - BEFORE):m.end() + AFTER]
        hit += [w for w in OTHER if w in near]
    # 「「Asile」は…最大8名まで、「OLILI」は…」のような棟の並列は文全体で見る
    if len(re.findall(r'[「『][^」』]{2,}[」』]\s*は', sent)) >= 2:
        hit.append("棟の並列")
    return sorted(set(hit))


def sentences(text, num):
    """人数を含む文だけを取り出す。句点で切る。"""
    out = []
    for part in re.split(r'(?<=。)', text):
        if re.search(NUM, part) and num in [zen(m) for m in re.findall(NUM, part)]:
            out.append(part.strip())
    return out


def main():
    show_all = "--all" in sys.argv
    idx = io.open('index.html', encoding='utf-8').read()
    villas = json.loads(re.search(r'const VILLAS=(\[.*?\]);', idx, re.S).group(1))
    spec = io.open('spec-data.js', encoding='utf-8').read()
    cell = {}
    for m in re.finditer(r'"(\d+)":\s*\{(.*?)\n  \}', spec, re.S):
        c = re.search(r'capacity:\s*\{([^{}]*)\}', m.group(2))
        if c:
            cell[m.group(1)] = c.group(1)

    rows = []
    for v in villas:
        vid = str(v['id'])
        cap = str(v.get('capacity') or '')
        if not cap.isdigit():
            continue
        for field in ('feature', 'desc'):
            text = v.get(field) or ''
            for raw in re.findall(NUM, text):
                n = zen(raw)
                if n == str(int(cap)):
                    continue
                sourced = 'url:' in cell.get(vid, '')
                if not sourced and not show_all:
                    continue
                rows.append((vid, v['name'], cap, n, field, sourced,
                             sentences(text, n)))
    print('紹介文の人数と capacity が食い違う箇所: %d 件' % len(rows))
    print('（capacity に出典があるものは、紹介文の側の誤りと確定できる）\n')
    for vid, name, cap, n, field, sourced, sents in rows:
        flags = sorted(set(w for s in sents for w in other_subject(s, n)))
        mark = ('  ← %s の人数の疑い' % '/'.join(flags)) if flags else ''
        if not sourced:
            mark += '  ★定員に出典なし'
        print('id=%-4s %-28s capacity=%-3s / %s に %s名%s'
              % (vid, name[:28], cap, field, n, mark))
        for s in sents:
            print('    「%s」' % s)
        print('')
    n_other = sum(1 for r in rows if any(other_subject(s, r[3]) for s in r[6]))
    print('-' * 68)
    print('うち %d 件は施設全体の定員以外（サウナ定員・棟別・日帰り等）を指す疑いがある。'
          % n_other)
    print('残り %d 件が、紹介文の側の誤りの候補。' % (len(rows) - n_other))


main()
