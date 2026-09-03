# -*- coding: utf-8 -*-
"""施設固有であるはずの項目に、複数施設で同じ出典URLを使っている箇所を洗い出す。

ブランド共通ページを開いて全施設に同じ値を振ると、棟・客室ごとの違いが潰れる。
「ブランド単位の一律適用は必ず間違える」（CLAUDE.md）ので、その痕跡を機械的に探す。

出るのは容疑であって誤りではない。ページが対象拠点を名指しで列挙していれば正当。
（例: SANU の MOSS型サウナ記事は5拠点を列挙しているので5施設に同じURLでよい）

  python3 tools/shared_src.py
"""
import io
import re
import collections

# 施設固有であるはずの項目。ブランド共通URLから機械的に振れないもの。
SPECIFIC = set("""capacity sauna_type stove coldbath loyly outdoor_rest
                  kitchen_type sauna_temp sauna_cap water_temp water_depth""".split())


def main():
    s = io.open('spec-data.js', encoding='utf-8').read()
    idx = io.open('index.html', encoding='utf-8').read()
    names = {}
    for m in re.finditer(r'"name":\s*"([^"]*)".{0,4000}?"id":\s*(\d+)', idx):
        names[m.group(2)] = m.group(1)

    url2 = collections.defaultdict(list)
    for m in re.finditer(r'"(\d+)":\s*\{(.*?)\n  \}', s, re.S):
        vid = m.group(1)
        for c in re.finditer(r'(\w+):\s*\{([^{}]*)\}', m.group(2)):
            k, cell = c.group(1), c.group(2)
            u = re.search(r"url:\s*'([^']*)'", cell)
            if u and k in SPECIFIC:
                url2[u.group(1)].append((vid, k))

    rows = []
    for u, lst in url2.items():
        ids = sorted(set(v for v, _ in lst), key=int)
        if len(ids) > 1:
            rows.append((len(ids), len(lst), u, ids,
                         sorted(set(k for _, k in lst))))
    rows.sort(reverse=True)

    print('施設固有の項目に同じ出典URLを使っている組み合わせ: %d 件' % len(rows))
    print('（容疑であって誤りではない。対象拠点を名指しするページなら正当）\n')
    for n, cells, u, ids, ks in rows:
        print('%d施設 / %d セル  %s' % (n, cells, u))
        print('    id: %s' % ', '.join(ids))
        print('    項目: %s' % ', '.join(ks))
        print('    施設: %s' % ' / '.join(names.get(i, '?')[:24] for i in ids))
        print('')


main()
