# -*- coding: utf-8 -*-
"""個別ページの <title> をデータから作り直す。

手で書いた定型が事実とずれていた。286件すべてが
「{県}のサウナ・温泉付き一棟貸しヴィラ」と言い切っていたが、
温泉タグを持つのは80件、客室サウナを持つのは255件しかない。

    python3 tools/fix_titles.py            差分を表示
    python3 tools/fix_titles.py --write    書き込む

サウナの語は sauna_exists で出し分ける。CLAUDE.md の判定基準どおり
yes/room だけが「客室にサウナがある」で、shared は共用設備、
未調査は「あるともないとも言えない」なので何も書かない。
"""
import re, sys, json, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def pref_jp():
    m = re.search(r'PREF_JP\s*=\s*(\{[^}]*\})', read('index.html'))
    return json.loads(m.group(1))


def lite():
    s = read('data/villas-lite.js')
    arr = json.loads(re.search(r'=\s*(\[.*\])\s*;?\s*$', s, re.S).group(1))
    return {v['i']: v for v in arr}


def sauna_exists():
    """spec-data.js を波括弧の対応で切り出す。空白数を決め打ちしない
    （CLAUDE.md: `(\\w+): \\{ v:` と書いて大半のセルを取りこぼした事故がある）。"""
    s = read('spec-data.js')
    out = {}
    for m in re.finditer(r'\n\s*"?(\d+)"?\s*:\s*\{', s):
        vid = int(m.group(1))
        p = m.end() - 1
        d = 0
        for j in range(p, len(s)):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    break
        blk = s[p:j + 1]
        mm = re.search(r"sauna_exists\s*:\s*\{\s*v\s*:\s*'([^']+)'", blk)
        out[vid] = mm.group(1) if mm else None
    return out


def esc(t):
    # 既存の題は施設名を HTML エスケープして埋め込んでいる。& だけでなく
    # アポストロフィも &#x27; になる（id=13 "Ocean's Terrace TORAMII"）。
    # & だけを見ていたときは8件、足して2件が照合に落ちた。
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&#x27;'))


def suffix(pj, se, tags):
    parts = []
    if se in ('yes', 'room'):
        parts.append('サウナ')
    elif se == 'shared':
        parts.append('共用サウナ')
    if 'onsen' in tags:
        parts.append('温泉')
    if parts:
        return '%sの%s付き一棟貸しヴィラ' % (pj, '・'.join(parts))
    return '%sの一棟貸しヴィラ・貸別荘' % pj


def main():
    write = '--write' in sys.argv
    PJ, L, SE = pref_jp(), lite(), sauna_exists()
    changed = skipped = 0
    from collections import Counter
    shapes = Counter()

    for f in sorted(glob.glob(os.path.join(ROOT, 'villas', '*.html'))):
        h = open(f, encoding='utf-8').read()
        mid = re.search(r'data-villa-id="(\d+)"', h)
        mt = re.search(r'<title>(.*?)</title>', h, re.S)
        if not (mid and mt):
            print('  ! 読めない: %s' % os.path.basename(f))
            skipped += 1
            continue
        vid = int(mid.group(1))
        v = L.get(vid)
        if not v:
            print('  ! villas-lite に無い id=%d' % vid)
            skipped += 1
            continue

        old = mt.group(1)
        # 施設名は villas-lite を正とする。名前に ｜ を含む施設があるので
        # （id=129「和モダングランピング｜NAGOMI CAMP」）末尾からは切らない。
        nm = esc(v['n'])
        if not old.startswith(nm + '｜'):
            print('  ! 施設名が題と合わない id=%d  題=%r  名=%r' % (vid, old, v['n']))
            skipped += 1
            continue

        new = '%s｜%s - villafaras' % (nm, suffix(PJ[v['p']], SE.get(vid), v.get('t') or []))
        shapes[suffix(PJ[v['p']], SE.get(vid), v.get('t') or []).split('の', 1)[1]] += 1
        if new == old:
            continue
        changed += 1
        if changed <= 12 or not write:
            print('  id=%-4d %s' % (vid, os.path.basename(f)))
            print('      - %s' % old)
            print('      + %s' % new)
        if write:
            open(f, 'w', encoding='utf-8').write(
                h[:mt.start(1)] + new + h[mt.end(1):])

    print()
    print('=== 題の型の内訳 ===')
    for k, n in shapes.most_common():
        print('  %4d  %s' % (n, k))
    print()
    print('変更 %d 件 / 読み飛ばし %d 件%s' % (changed, skipped, '' if write else '（--write で書き込み）'))


main()
