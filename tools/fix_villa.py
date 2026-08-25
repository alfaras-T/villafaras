#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys

# set_villa で触る VILLAS のスカラー項目。villas/*.html では fact 行としても描画される。
VILLA_FACTS = {
    "capacity": ("定員", "%s名"),
    "checkin":  ("チェックイン", "%s"),
    "checkout": ("チェックアウト", "%s"),
}


def json_obj_end(s, i):
    """JSON オブジェクトの開き波括弧 i から、対応する閉じ括弧の次の位置を返す。"""
    if i < 0 or i >= len(s) or s[i] != "{":
        return -1
    depth = 0
    while i < len(s):
        c = s[i]
        if c == '"':
            i += 1
            while i < len(s) and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1

FIXES = {
    "143": {"name": "mysa hakone",
            "reason": "capacity=9 は OTA の定員欄の仕様上限。公式コンセプトページに「最大宿泊可能人数：12人」「最大12名宿泊可能」とあり 12 が正しい。あわせてサウナイキタイで水風呂・熱源・室温・定員を確認した。「水風呂 収容人数：2人 水深80~110cm 1人用の、肩まで浸かれるプールが2つ置いております。季節によって温度は変わります。秋〜春は15℃、冬はシングルになります。」「サウナ室 温度80度 収容人数：10人 ドライサウナ 薪」「●外気浴 デッキチェア: 8席」（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "capacity":   {"v": 12, "src": "desk", "at": "2026-08",
                                        "url": "https://hotel-mysa.com/concept/"},
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel-mysa.com/concept/"},
                         "loyly":      {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel-mysa.com/concept/"},
                         "coldbath":   {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "stove":      {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "sauna_temp": {"v": 80, "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "sauna_cap":  {"v": 10, "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "water_depth":{"v": "shoulder", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "outdoor_rest":{"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "rest_chair": {"v": "chair", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"},
                         "wifi":       {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://sauna-ikitai.com/saunas/63970"}}},

    "162": {"name": "プライベートヴィラ愛川",
            "reason": "capacity=5 は誤り。公式の客室ページに「定員 １棟につき10名（添い寝のお子様除く）」とあり、ベッド構成「クイーンベッド１台、ダブルベッド4台、ソファーベット5台」とも整合する。同ページの施設内設備が列挙形式で「貸切露天ジャグジー風呂・サウナ、浴室、水風呂、屋根付きBBQガーデン…全館Wi-Fi完備」とあり、ジャグジーとは別に水風呂が独立して挙がっているため coldbath=bath。「セルフロウリュも可能なバレルサウナとジャグジーを設置」「IHコンロ3口、鍋用IHコンロ」（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity":    {"v": 10, "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"},
                         "coldbath":    {"v": "bath", "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"},
                         "loyly":       {"v": "yes", "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"},
                         "outdoor_rest":{"v": "yes", "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"},
                         "kitchen_type":{"v": "ih", "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"},
                         "wifi":        {"v": "yes", "src": "desk", "at": "2026-08",
                                         "url": "https://withthedogs.jp/villa"}}},

    "171": {"name": "Noёl HAKONE GENSEN",
            "reason": "capacity=9 は一休の定員欄の仕様上限で誤り。同じページのプラン名が「最大20名様、1棟貸しプラン」、本文に「・最大定員：16名様（エアーマットレス併用で最大20名様）」「本施設は最大20名様まで宿泊可能ですが、一休のサイト仕様上9名様しか予約ができません。10名以上の場合は別途ご連絡下さい。」とある。範囲は上限を採る規約に従い 20 とする（エアーマットレスなしの通常定員は16）（2026-08確認）",
            "set_villa": {"capacity": "20"},
            "set_spec": {"capacity": {"v": 20, "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/vacation/00051638/11400824/10235981/"}}},

    "170": {"name": "Six on the Beach TORAMII -Enoshima-",
            "reason": "index.html の capacity が 9、spec-data.js が 12 で食い違っていた。公式に「お1人様から最大12名様までご自由にご利用いただけます」とあり spec-data.js 側の 12 が正しい。index.html と個別ページを合わせる。あわせて屋外設備の列挙「星空ジャグジー、サウナ、WeberBBQグリル、エコスマートファイヤー、温水シャワー、ダイニングシステムなど全て無料でご利用いただけます」より outdoor_rest=yes、室内設備「キッチン用品（IHコンロ）」より kitchen_type=ih（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {
                         "outdoor_rest":{"v": "yes", "src": "desk", "at": "2026-08",
                                         "url": "https://toramii.jp/enoshima/"},
                         "kitchen_type":{"v": "ih", "src": "desk", "at": "2026-08",
                                         "url": "https://toramii.jp/enoshima/"}}},
}

DRY = "--dry-run" in sys.argv


def write(path, s, orig):
    if s == orig:
        print("    変更なし: %s" % path)
        return 0
    if DRY:
        print("    [dry-run] %s を更新予定" % path)
    else:
        io.open(path, "w", encoding="utf-8").write(s)
        print("    更新: %s" % path)
    return 1


for vid, fx in FIXES.items():
    print("\n=== id=%s %s ===" % (vid, fx["name"]))
    print("  理由: %s" % fx["reason"])

    p = "index.html"
    s = orig = io.open(p, encoding="utf-8").read()
    villas = json.loads(re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL).group(1))
    tgt = [v for v in villas if str(v["id"]) == vid]
    if not tgt:
        print("  !! VILLAS に見つかりません"); continue
    cur_tags = tgt[0].get("tags") or []

    for t in fx.get("remove_tags", []):
        if t not in cur_tags:
            print("    tag '%s' は既にありません" % t); continue
        new_tags = [x for x in cur_tags if x != t]
        # 同じタグ構成の別施設を誤爆しないよう、対象施設のオブジェクト内に限定して置換する。
        # VILLAS の各要素は tags -> id の順に並ぶので、"id": N の直前の "tags": [...] が対象。
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        cands = list(re.finditer(r'"tags":\s*(\[[^\]]*\])', s[:mid.start()]))
        if not cands:
            print("    !! tags が見つかりません"); continue
        last = cands[-1]
        if json.loads(last.group(1)) != cur_tags:
            print("    !! tags が一致しません（%s）" % last.group(1)); continue
        rep = json.dumps(new_tags, ensure_ascii=False)
        if '", "' not in last.group(1):
            rep = rep.replace('", "', '","')
        s = s[:last.start(1)] + rep + s[last.end(1):]
        print("    tags: %s -> %s" % (cur_tags, new_tags))
        cur_tags = new_tags

    # VILLAS のスカラー項目。同じ値を持つ別施設を誤爆しないよう、
    # "id": N を含む施設オブジェクトの範囲内に限定して置換する。
    old_vals = {}
    for k, val in (fx.get("set_villa") or {}).items():
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        st = s.rfind('{"name"', 0, mid.start())
        en = json_obj_end(s, st)
        if st < 0 or en < 0:
            print("    !! id=%s の施設オブジェクト範囲を特定できません" % vid); continue
        seg = s[st:en]
        mk = re.search(r'("%s":\s*)"([^"]*)"' % re.escape(k), seg)
        if not mk:
            print("    !! %s が見つかりません" % k); continue
        if mk.group(2) == str(val):
            print("    %s は既に %s" % (k, val)); continue
        print("    %s: %s -> %s" % (k, mk.group(2), val))
        old_vals[k] = mk.group(2)
        s = s[:st] + seg[:mk.start()] + '%s"%s"' % (mk.group(1), val) \
            + seg[mk.end():] + s[en:]

    if fx.get("old_desc"):
        n = s.count(fx["old_desc"])
        if n:
            s = s.replace(fx["old_desc"], fx["new_desc"])
            print("    desc: %d 箇所を差し替え" % n)
        else:
            print("    !! desc が一致しません（index.html）")
    write(p, s, orig)

    for p in glob.glob("villas/%s-*.html" % vid):
        s = orig = io.open(p, encoding="utf-8").read()
        if fx.get("old_desc"):
            s = s.replace(fx["old_desc"], fx["new_desc"])
            for t in set(re.findall(r'content="([^"]{40,}?)…"', s)):
                if t and fx["old_desc"].startswith(t):
                    s = s.replace(t + "…", fx["new_desc"][:len(t)] + "…")
                    print("    meta 短縮版を差し替え")
        for k, val in (fx.get("set_villa") or {}).items():
            # fact 行ではないが本文中にそのまま出る項目（official など）は
            # 旧い値を新しい値に置き換える。個別ページは1施設分なので誤爆しない。
            if k not in VILLA_FACTS:
                old = old_vals.get(k)
                if old and old in s:
                    n = s.count(old)
                    s = s.replace(old, val)
                    print("    %s を %d 箇所差し替え -> %s" % (k, n, val))
                continue
            label, fmt = VILLA_FACTS[k]
            new = fmt % val
            s2 = re.sub(r'(<span class="fact-label">%s</span>'
                        r'<span class="fact-val">)[^<]*(</span>)' % re.escape(label),
                        lambda m: m.group(1) + new + m.group(2), s, count=1)
            if s2 != s:
                print("    fact「%s」を %s に更新" % (label, new))
                s = s2

        for t in fx.get("remove_tags", []):
            label = {"sauna": "サウナ", "pet": "ペットOK", "bbq": "BBQ",
                     "onsen": "温泉", "pool": "プール"}.get(t)
            if label:
                s2 = re.sub(r'<span class="pill"[^>]*>' + re.escape(label) + r'</span>',
                            "", s, count=1)
                if s2 != s:
                    print("    pill「%s」を削除" % label)
                    s = s2
        write(p, s, orig)

    p = "spec-data.js"
    s = orig = io.open(p, encoding="utf-8").read()
    m = re.search(r'(^  "%s": \{.*?\n  \},?)' % vid, s, re.M | re.S)
    if m:
        blk = m.group(1)
        nb = blk
        for k in fx.get("remove_spec", []):
            nb = re.sub(r"\n    %s:\s*\{[^}]*\},?" % re.escape(k), "", nb)
        for k, val in (fx.get("set_spec") or {}).items():
            body = "{ " + ", ".join(
                "%s: %s" % (kk, json.dumps(vv, ensure_ascii=False).replace('"', "'")
                            if isinstance(vv, str) else vv)
                for kk, vv in val.items()) + " }"
            mk = re.search(r"\n(\s*)%s:(\s*)\{[^}]*\}" % re.escape(k), nb)
            if mk:
                old = mk.group(0)
                new = "\n%s%s:%s%s" % (mk.group(1), k, mk.group(2), body)
                if old != new:
                    nb = nb.replace(old, new, 1)
                    print("    spec: %s を更新 -> %s" % (k, body))
                else:
                    print("    spec: %s は既に同値" % k)
            else:
                nb = nb.replace("\n  },", "\n    %s: %s,\n  }," % (k, body), 1) \
                     if "\n  }," in nb else nb
                print("    spec: %s を追加 -> %s" % (k, body))
        nb = re.sub(r",(\s*\n  \},)", r"\1", nb)
        # 項目を追加したとき、それまで最後だった項目にはカンマが無い。
        # 補わないと "}" の直後に次の項目が続いて JS の構文エラーになる。
        # 波括弧の対応は取れてしまうので validate.py の括弧検査では気づけない。
        nb = re.sub(r"\}\n(\s+)(\w+):", r"},\n\1\2:", nb)
        if nb != blk:
            s = s.replace(blk, nb, 1)
            if fx.get("remove_spec"):
                print("    spec: %s を削除" % ", ".join(fx["remove_spec"]))
        write(p, s, orig)
    else:
        print("    spec-data.js に該当なし")

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
