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
    "1": {"name": "古民家宿るうふ 清之家",
            "reason": "capacity=9 は誤り。「2名〜10名様までご利用いただけます」より 10 に訂正。寝具（シングル4・ダブル2・布団2＝10）と整合。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://loof-inn.com/hotels/seinoie"}}},

    "13": {"name": "Ocean's Terrace TORAMII",
            "reason": "capacity=9 は誤り。「お1人様から最大12名様までご自由にご利用いただけます。」より 12 に訂正。料金表も「1～4名様」「5～12名様」の2区分。DB紹介文の「最大14名」は誤り。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://toramii.jp/oceans-terrace-toramii/"}}},

    "22": {"name": "海都-kaito- TOKYOBAY",
            "reason": "capacity=9 は誤り。「客室定員 12名 推奨人数7名」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://piyoresort.com/kaito/room/"}}},

    "23": {"name": "The TRAVELERS Chateau Tateyama",
            "reason": "capacity=9 は誤り。「一棟貸し（3LDK）最大10名様 禁煙」より 10 に訂正。公式URLがInstagramだったため実サイトを特定。要URL訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://yamato-stay.com/the-travelers-chateau-tateyama"}}},

    "44": {"name": "久留里山荘（QULRI SANSO）",
            "reason": "capacity=9 は誤り。「最大10名様までの宿泊が可能」より 10 に訂正。公式サイトが存在せずOTAのみ。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00051772/"}}},

    "52": {"name": "緑邸～OHTAKI～",
            "reason": "capacity=9 は誤り。「最大で10名様が宿泊可能」より 10 に訂正。料金ページも4名〜10名の段階料金。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://www.ryokutei.jp/facility"}}},

    "66": {"name": "Villa Yno",
            "reason": "capacity=9 は誤り。「定員：最大10名（セミダブルベッド×4台、敷布団×2組）」より 10 に訂正。公式サイト未発見。同ページの「定員：1名～9名」は一休系の仕様上限。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00052212/room/"}}},

    "83": {"name": "THE TIME FUJI",
            "reason": "capacity=9 は誤り。「宿泊人数は7名様までとなっております。」より 7 に訂正。前回 一休「定員 1名～9名」を根拠に9としたのは誤り。一休の定員欄は9名が仕様上限で実定員ではない。施設自身の予約サイトで7名を確認。（2026-08確認）",
            "set_villa": {"capacity": "7"},
            "set_spec": {"capacity": {"v": 7, "src": "desk", "at": "2026-08",
                                      "url": "https://thetime.snack.chillnn.com/ja/snack/6c870504-3e7c-49b8-b172-6efd732e4704"}}},

    "84": {"name": "mysa fuji",
            "reason": "capacity=9 は誤り。「最大宿泊可能人数：10人」より 10 に訂正。「9名以上でご宿泊の場合は折り畳みマットレス2台をご利用ください」と整合。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://hotel-mysa-fuji.com/concept/"}}},

    "85": {"name": "mysa yamanakako",
            "reason": "capacity=9 は誤り。「折りたたみマットレスをご用意しておりますので、5名以上でご宿泊の場合はそちらをご利用ください。（最大10名）」より 10 に訂正。公式サイト未発見。姉妹施設 mysa fuji（公式で10確認済み）と同型。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00052086/room/"}}},

    "98": {"name": "SILVER SPRAY 山中湖",
            "reason": "capacity=9 は誤り。「最大10名まで宿泊可能です」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://silver-spray.jp/cottage.php"}}},

    "101": {"name": "KURA YARD",
            "reason": "capacity=9 は誤り。「最大15名まで泊まれる大きな家」より 15 に訂正。DB紹介文の「最大13名」とも食い違う。公式が15。（2026-08確認）",
            "set_villa": {"capacity": "15"},
            "set_spec": {"capacity": {"v": 15, "src": "desk", "at": "2026-08",
                                      "url": "https://kurayard.com"}}},

    "103": {"name": "Private villa FujiNagi",
            "reason": "capacity=9 は誤り。「定員 10名（子供料金のかかるお子様も含む）」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://www.fujinagi.com/overview-facility.html"}}},

    "107": {"name": "ReTune | SPA & SAUNA / VILLA",
            "reason": "capacity=9 は誤り。「宿泊 10名迄」より 10 に訂正。公式はJS描画で取得不可。紹介文の「8人まで」はテントサウナの定員で別項目。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://kawaguchiko.e-villa.jp/capacity/10.html"}}},

    "121": {"name": "COCO VILLA 那須高原",
            "reason": "capacity=9 は誤り。「最大利用人数 12名 ※ 推奨人数は6名です」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/nasu-kogen/"}}},

    "140": {"name": "ルクス箱根湯本 LUX HAKONE YUMOTO",
            "reason": "capacity=9 は誤り。「最大定員11名です。ベッド数は、ダブルベッド2台、シングルベッド3台、ダブル布団2組（畳ロフト）となります。」より 11 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "11"},
            "set_spec": {"capacity": {"v": 11, "src": "desk", "at": "2026-08",
                                      "url": "https://lux-hakone.com/faq/"}}},

    "142": {"name": "プライベートリゾート仙居",
            "reason": "capacity=9 は誤り。「6LDK・最大16名対応。」より 16 に訂正。施設独自サイト https://hakone-senkyo.com/ を発見（要URL訂正）。（2026-08確認）",
            "set_villa": {"capacity": "16"},
            "set_spec": {"capacity": {"v": 16, "src": "desk", "at": "2026-08",
                                      "url": "https://beds24.com/booking.php?propid=283750"}}},

    "149": {"name": "MOROISOSO-サウナ＆温水プール付きラグジュアリーヴィラ",
            "reason": "capacity=9 は誤り。「4ベッドルームで最大18名まで利用可能です。」より 18 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "18"},
            "set_spec": {"capacity": {"v": 18, "src": "desk", "at": "2026-08",
                                      "url": "https://moroisoso.jp"}}},

    "183": {"name": "Hakuba Amber Resort",
            "reason": "capacity=9 は誤り。「最大12名 3LDKでゆったり家族風呂付きシャレー／お布団を追加購入（5,500円/式）することで最大12名まで対応可能」より 12 に訂正。公式サイトなし（Jade Group はリンク集のみ）。プラン名の数字は仕様上限とは別系統。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/00051318/"}}},

    "188": {"name": "COCO VILLA 軽井沢",
            "reason": "capacity=9 は誤り。「最大利用人数：12名」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/karuizawa/"}}},

    "212": {"name": "熱海リゾート",
            "reason": "capacity=9 は誤り。「定員 10名」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://www.resolstay.jp/details/atamiresort/"}}},

    "234": {"name": "COCO VILLA 伊豆赤沢",
            "reason": "capacity=9 は誤り。「最大利用人数：10名 ※ 推奨人数は7名です」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/izuakazawa/"}}},

    "243": {"name": "Azure Palace 伊豆高原",
            "reason": "capacity=9 は誤り。「収容人数 14名まで可能／FAQ「最大収容人数何名でしょうか？14名までご宿泊可能です。」」より 14 に訂正。ページ内住所「伊東市富戸1317-4479」で近接する別施設との取り違えがないことを確認。（2026-08確認）",
            "set_villa": {"capacity": "14"},
            "set_spec": {"capacity": {"v": 14, "src": "desk", "at": "2026-08",
                                      "url": "https://azurepalace.net"}}},

    "245": {"name": "villa 緑と物語",
            "reason": "capacity=9 は誤り。「定員：最大10名」より 10 に訂正。公式はJS描画で取得不可。OTA部屋名も「10名様まで宿泊可」。同ページの「1名～9名」は仕様上限。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://prtimes.jp/main/html/rd/p/000000001.000154491.html"}}},

    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "capacity=9 は誤り。「定員： 10人」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://luxevillas-izu.com/stay/sana-izuomuroyama/"}}},

    "250": {"name": "プライベートリゾート南風",
            "reason": "capacity=9 は誤り。「最大11名様まで滞在可能」より 11 に訂正。登録URL https://izu-nao.com/t は誤り（要URL訂正）。同ページの「定員 1名～9名」は仕様上限。（2026-08確認）",
            "set_villa": {"capacity": "11"},
            "set_spec": {"capacity": {"v": 11, "src": "desk", "at": "2026-08",
                                      "url": "https://izu-nao.com/"}}},

    "270": {"name": "COCO VILLA 長瀞",
            "reason": "capacity=9 は誤り。「最大利用人数 12名 ※ 推奨人数は8名です」より 12 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "12"},
            "set_spec": {"capacity": {"v": 12, "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/nagatoro/"}}},

    "276": {"name": "COCO VILLA 大洗",
            "reason": "capacity=9 は誤り。「最大利用人数：10名 / 推奨人数は5名です」より 10 に訂正。（2026-08確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {"capacity": {"v": 10, "src": "desk", "at": "2026-08",
                                      "url": "https://coco-villa.jp/villa/oarai/"}}},
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
