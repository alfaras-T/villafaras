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
    "2": {"name": "古民家宿るうふ 波之家",
          "reason": "2026-08 に sauna_exists を no へ訂正した際、2026-07 に入れた sauna_type='tent' が残っていた。サウナが無い施設に形式だけが残るのは矛盾なので削除する。tools/validate.py が検出（2026-08）",
          "remove_spec": ["sauna_type"]},

    "13": {"name": "Ocean's Terrace TORAMII",
           "reason": "sauna_temp に範囲文字列 '80〜90' が入っており、単位 ℃ の数値項目に文字列が入っていた。公式サイトに「2022年夏にヒノキのサウナ小屋を新設しました！」「80〜90度まで自動上昇する電気式なので手間いらず。」とあり、範囲表記は上限を採る方針で 90 とする。あわせて出典URLを記録（2026-08確認）",
           "set_spec": {"sauna_temp": {"v": 90, "src": "desk", "at": "2026-08",
                                       "url": "https://toramii.jp/oceans-terrace-toramii/"}}},

    "133": {"name": "GEOSPOT MOTOHAKONE B",
            "reason": "coldbath に選択肢マスタに存在しない値 'cold' が入っていた。公式サイトの「設備」に「水風呂」、EXPERIENCES 02 に「全客室の2階に、プライベートサウナと水風呂、外気浴が楽しめるテラスを設置。」とあり bath が正しい。全客室と明記されているため A/B/C に共通で適用できる（2026-08確認）",
            "set_spec": {"coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                      "url": "https://geo-spot.com/motohakone/"}}},

    "134": {"name": "GEOSPOT MOTOHAKONE C",
            "reason": "同上。coldbath='cold' は選択肢マスタに無い値。公式サイト「全客室の2階に、プライベートサウナと水風呂、外気浴が楽しめるテラスを設置。」より bath に訂正（2026-08確認）",
            "set_spec": {"coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                      "url": "https://geo-spot.com/motohakone/"}}},

    "172": {"name": "Oyado S",
            "reason": "water_temp に選択肢型ではない '10〜18' が入っていた。公式予約サイトの注意事項「サウナについて」に水温の記載はなく、「水風呂の水は、使用後は止めてください。大切な資源です。」とあり掛け流し方式で通年の水温が変動する。water_temp は「夏場の水温」の選択肢型（u10/t1015/t1518/t1822/o22）であり、通年レンジはどの区分にも割り当てられないため未調査に戻す（2026-08確認）",
            "remove_spec": ["water_temp"]},

    "175": {"name": "軽井沢365 リバーサイドヴィラ八風台",
            "reason": "capacity=6 が誤り。公式サイトの施設情報に「宿泊人数 1-12名／推奨4名-10名」「*11名から敷布団をご用意」とあり定員は12名。各棟一覧でも「4-10名様以上向け（ River Side Villa Happudai ）」と表記されている。推奨人数10名（comfort_cap）は正しく、定員のほうが誤っていた。軽井沢365は5棟あり棟ごとに仕様が異なる（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://karuizawa365.jp/stay/riversidevilla"}}},

    "197": {"name": "トライハク軽井沢 神楽-かぐら-",
            "reason": "capacity=4 が誤り。公式「施設・設備」ページの諸元表に「間取り 3LDK／宿泊人数 推奨6名（最大14名まで）／ベッド数 ダブルベッド6台 + シングル布団2台／敷地面積 約700㎡（約210坪）」とあり定員は14名。敷地約700㎡は紹介文の「700平米専有」と一致し、3施設（ひなた/ゆずき/かぐら）のうちかぐらの表であることを確認済み。推奨6名（comfort_cap）は正しい（2026-08確認）",
            "set_villa": {"capacity": "14"},
            "set_spec": {"capacity": {"v": 14, "src": "desk", "at": "2026-08",
                                      "url": "https://www.tryhaku.jp/rooms/"}}},
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
            if k not in VILLA_FACTS:
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
        if nb != blk:
            s = s.replace(blk, nb, 1)
            if fx.get("remove_spec"):
                print("    spec: %s を削除" % ", ".join(fx["remove_spec"]))
        write(p, s, orig)
    else:
        print("    spec-data.js に該当なし")

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
