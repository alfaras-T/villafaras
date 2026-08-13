#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys

FIXES = {
    # --- 一部客室のみサウナ付き（棟／客室タイプでサウナの有無が分かれる）
    "73": {"name": "SANU 2nd Home 南アルプス1st",
            "reason": "宿泊者記録に「サウナ付きキャビンに2泊」。全12棟のうち一部のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052337/"}}},
    "75": {"name": "SANU 2nd Home 八ヶ岳3rd",
            "reason": "公式紹介文に「プライベートサウナと水風呂を備えた部屋もあり」。一部客室のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052073/"}}},
    "76": {"name": "SANU 2nd Home 河口湖2nd",
            "reason": "全15室中「サウナ付き客室【富士山ビュー】」が一客室タイプとして分離販売（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052074/"}}},
    "118": {"name": "SANU 2nd Home 那須1st",
            "reason": "OTAの客室一覧に SANU CABIN BEE と SANU CABIN WITH SAUNA が並存。サウナは一部棟のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052026/11555802/10277047/"}}},
    "119": {"name": "SANU 2nd Home 那須2nd",
            "reason": "サウナ付き客室が個別プランとして分離販売。サウナは一部棟のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://travel.yahoo.co.jp/00052027/room/"}}},
    "120": {"name": "SANU 2nd Home 那須3rd",
            "reason": "公式紹介文に「部屋タイプによってはサウナや露天風呂も楽しめ」とあり一部客室のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052290/"}}},
    "176": {"name": "SANU 2nd Home 北軽井沢2nd",
            "reason": "一休の客室区分が「サウナ付き客室」。サウナは独立棟で一部のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052029/11555912/10277648/"}}},
    "177": {"name": "SANU 2nd Home 蓼科1st",
            "reason": "「サウナ付き客室」プランが分離販売。一部客室のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052266/11641728/10292977/"}}},
    "178": {"name": "SANU 2nd Home 軽井沢2nd",
            "reason": "公式紹介文に「サウナ付き客室あり」。一部客室のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052415/"}}},
    "179": {"name": "SANU 2nd Home 白馬1st",
            "reason": "全5棟のうちサウナ付きは1棟のみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/00052076/"}}},
    "246": {"name": "SANU 2nd Home 伊豆1st",
            "reason": "SANU公式に「露天風呂：全室設置／プライベートサウナ：4室」「プライベートサウナは一部の客室のみ」と明記。全16室中4室（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.sa-nu.com/list/raym_izu1st"}}},
    "248": {"name": "エンゼルフォレスト中伊豆",
            "reason": "予約システムに「デラックス（サウナ付き）」が独立客室タイプとして存在。全15室のうち一部のみ。姉妹施設の那須と同型（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://reserve.489ban.net/client/ang-n/0/plan/room/37807"}}},
    "257": {"name": "THE GLAMPING 箱根十国峠",
            "reason": "フィンランドサウナ付きの「サウナスイートヴィラ」を含む4タイプ15棟。サウナがあるのは1タイプのみ（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.jukkoku-cable.jp/glamping/"}}},
    "191": {"name": "軽井沢 HOUSE VILLA",
            "reason": "全6棟のうちサウナと水風呂を備えるのは「サウナ棟」のみ。他棟は足湯棟・檜風呂棟等（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://karuizawa-house-villa.com"}}},
    "285": {"name": "上小川レジャーペンション",
            "reason": "共用の貸切「森のSAUNA」に加え、2025年8月新設の「半露天風呂・サウナ付コテージ メープル」のみ客室内サウナあり（2026-08確認）",
            "set_spec": {"sauna_exists": {"v": "room", "src": "desk", "at": "2026-08",
                                          "url": "https://www.cottagelife.jp/ibaraki/la100200/id5473.html"}}},

    # --- 共用サウナのみ。shared はトップの絞り込み対象外なので sauna タグも外す。
    "129": {"name": "和モダングランピング｜NAGOMI CAMP",
            "reason": "全4棟共用のバレルサウナ1基を時間制・別料金（3,500円/組・定員2名）で貸切利用する方式（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://www.glamping-tochigi.com/"}}},
    "272": {"name": "ノーラ名栗",
            "reason": "ナイトサウナは他の宿泊者との共同利用。日帰りサウナ客も受け入れており客室内サウナではない（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://travel.rakuten.co.jp/HOTEL/188834/188834.html"}}},
    "284": {"name": "ALOHA GLAMPING RESORT SAKAI",
            "reason": "公式サイトに「敷地内にはアウトドアサウナと外気浴用ととのいチェアを設置」。コテージ4棟＋テント12区画に対し敷地内サウナ1基（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ibaraki-sakai-glamping.com/"}}},
    "283": {"name": "THE BOTANICAL RESORT 林音",
            "reason": "サウナは共用温浴施設「りんねの湯」に集約（サウナガーデン／女湯1・男湯2）。日帰り利用も可。全45棟の客室側にサウナの記載なし（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://rinne-resort.jp/rinnenoyu"}}},
    "130": {"name": "那須温泉グランピング Nenn",
            "reason": "館内設備の「大浴場(サウナ付き)」を時間制で共用（15:00-23:30／翌7:00-9:30）。全17室にあるのはヴィンテージバス（浴槽）でサウナではない（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://travel.rakuten.co.jp/HOTEL/184489/184489.html"}}},
    "128": {"name": "Haga Farm＆Glamping",
            "reason": "公式に「プールサイドには『森のバレルサウナ』…グループ単位での貸切」。グランピング10棟に対し1基を予約制で共用（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://hagafarm.com/experience/"}}},
    "115": {"name": "有形文化財ホテル 飯塚邸",
            "reason": "独立サウナ棟「里鎮」を6棟で共有。完全予約・1組貸切90分の2枠制で、土蔵・文庫蔵の宿泊者は1名2,200円の別料金。日帰り枠もあり（2026-08確認）",
            "remove_tags": ["sauna"],
            "set_spec": {"sauna_exists": {"v": "shared", "src": "desk", "at": "2026-08",
                                          "url": "https://travel.yahoo.co.jp/00050899/"}}},

    # --- サウナ提供終了（過去の訂正で tag は削除済みだが spec が残存していた）
    "2": {"name": "古民家宿るうふ 波之家",
          "reason": "テントサウナは2026-01-16をもって提供終了（楽天トラベルの公式告知）。spec-data.js に sauna_exists: yes が残存していたため no を明示（2026-08確認）",
          "set_spec": {"sauna_exists": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://travel.rakuten.co.jp/HOTEL/183522/183522.html"}}},
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
