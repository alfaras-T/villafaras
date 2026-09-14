#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys
import urllib.parse

# ota のキーと、villas/*.html のボタンに出るラベルの対応。
# 個別ページの ota リンクは URL の文字列置換では特定できない。
#   (a) 旧い値が別のURLの前方一致になる（id=113 の agoda "https://ash-villa.com/" は
#       公式リンク "https://ash-villa.com/?utm_source=GBP..." の前方一致で、
#       公式リンクまで Agoda のURLに書き換わるところだった）
#   (b) 2つのキーが同じURLを持つ（id=246 は ikyu と agoda が両方 00052094 だった）
# どちらもラベルで対象を特定すれば起きない。
OTA_LABEL = {"ikyu": "一休.com", "rakuten": "楽天トラベル", "booking": "Booking.com",
             "agoda": "Agoda", "airbnb": "Airbnb", "expedia": "Expedia"}


def esc(u):
    """index.html は生のURL、villas/*.html は HTML エスケープ済み。"""
    return u.replace("&", "&amp;")


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
    "155": {"name": "SAJIMA Funny house",
            "reason": '**楽天の設備ページを全件走査したときに、ページ上の住所とDBの `addr` を照合して見つけた。** 192施設ぶんの独立した住所が同じページに載っているので、照合そのものは追加コスト0だった。（2026-09確認）\n\n`ota.rakuten` が **`HOTEL/188882` = 「ZUSHI Funny house」（逗子市新宿2-13-20）** を指していた。DB は横須賀市佐島3-12-41 で、**同じ Funny グループの別施設**である。\n\n正しいページは **`HOTEL/189434`「SAJIMA Funny house／民泊」**で、住所は「〒240-0103 神奈川県横須賀市**佐島3-12-41**」とDBに完全一致した。差し替えた。\n\n同ブランドは HAYAMA / MORITO / ZUSHI / CAP MARTIN / PREMIUM / SAJIMA と施設名の形が揃っているので、**番号が隣接していても中身は別施設**になる（id=6 CAP MARTIN は `188884`、この誤りは `188882`）。',
            "set_villa": {"rakuten": "https://travel.rakuten.co.jp/HOTEL/189434/189434.html"},
            },
    "278": {"name": "LUCY RESORT（ルーシー リゾート）",
            "reason": '**楽天の設備ページを全件走査したときに、ページ上の住所とDBの `addr` を照合して見つけた。** 192施設ぶんの独立した住所が同じページに載っているので、照合そのものは追加コスト0だった。（2026-09確認）\n\n`ota.rakuten` の `HOTEL/189751` は「**指定されたページは掲載終了しました**」を返す。検索索引には残っているが、`189751.html` も `hotelinfo/plan/189751` も生きていない。\n\n**楽天トラベルキャンプに移っていた。** `camp.travel.rakuten.co.jp/properties/1024` が「〒300-2661 茨城県つくば市**上河原崎39-1**」とDBに完全一致する（実機で確認。静的HTMLには住所が無く、JS描画後にしか出ない）。\n\n**ドメインが `travel.rakuten.co.jp` でなくても楽天トラベルの施設ページである。**id=26 の `vacation-stay.jp`（楽天LIFULL STAY）と同じ扱いにした。',
            "set_villa": {"rakuten": "https://camp.travel.rakuten.co.jp/properties/1024"},
            },
    "239": {"name": "AMAO VILLA",
            "reason": '**楽天の設備ページを全件走査したときに、ページ上の住所とDBの `addr` を照合して見つけた。** 192施設ぶんの独立した住所が同じページに載っているので、照合そのものは追加コスト0だった。（2026-09確認）\n\n`ota.rakuten` が **`HOTEL/189659` = 「AMAO VILLA 熱海」（熱海市伊豆山1165-201）** を指していた。DB は伊東市富戸911-122 である。\n\n**id=239 で混線が見つかった5つ目のフィールド。** これまでに `addr`（伊豆高原の住所）、`feature`（城ヶ崎の紹介文）、`desc`（熱海の紹介文）を訂正しており、`official` と `ota.ikyu` だけが富戸を指していた。**姉妹施設4つが1エントリに混ざっている。**\n\n**差し替え先が無い。** 楽天に載っているのは熱海（`189659`）と伊豆高原（`187204`・富戸**1007-32**）の2件だけで、**富戸911-122 の登録が無い**。なお `187204` の住所は、訂正前に id=239 の `addr` に入っていた値そのものである。\n\n方針どおり削除した。agoda / booking / ikyu は富戸を指しており残る。',
            "remove_ota": ["rakuten"],
            },
    "83":  {"name": "THE TIME FUJI",
            "reason": '**楽天の設備ページを全件走査したときに、ページ上の住所とDBの `addr` を照合して見つけた。** 192施設ぶんの独立した住所が同じページに載っているので、照合そのものは追加コスト0だった。（2026-09確認）\n\n`ota.rakuten` の `HOTEL/186838` は「**指定されたページは掲載終了しました**」を返す。`186838.html` / `hotelinfo/plan/186838` / `rtmap.html` のいずれも生きていない。\n\n検索索引には残っているが別番号での再登録は見つからなかった。削除した。agoda / airbnb / booking / ikyu は残る。\n\n**この施設は定員をめぐって一度誤った判断をしている。** 一休の「定員 1名〜9名」を根拠に9としたが、施設自身の予約サイトの「7名様までとなっております。」が正しかった。',
            "remove_ota": ["rakuten"],
            },
    "285": {"name": "上小川レジャーペンション",
            "reason": '**楽天の設備ページを全件走査したときに、ページ上の住所とDBの `addr` を照合して見つけた。** 192施設ぶんの独立した住所が同じページに載っているので、照合そのものは追加コスト0だった。（2026-09確認）\n\n`ota.rakuten` の `HOTEL/171882/` は **HTTP 404**。`rtmap.html` も 404 で、掲載終了の案内すら出ない（楽天は掲載終了と404を出し分けている）。\n\n別番号での再登録は見つからなかった。削除した。**残るのは jalan だけになる。**',
            "remove_ota": ["rakuten"],
            },
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

    for t in fx.get("add_tags", []):
        if t in cur_tags:
            print("    tag '%s' は既にあります" % t); continue
        new_tags = cur_tags + [t]
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

    # ota のキーごと削除する。壊れたリンク（広告中継URL、検索結果ページ、
    # 別施設を指すもの）を消すための操作。値の置換は set_villa で足りるが、
    # キーの削除はできないため分けてある。
    for k in (fx.get("remove_ota") or []):
        mid = re.search(r'"id":\s*%s\s*[,}]' % vid, s)
        if not mid:
            print("    !! id=%s が index.html に見つかりません" % vid); continue
        st = s.rfind('{"name"', 0, mid.start())
        en = json_obj_end(s, st)
        if st < 0 or en < 0:
            print("    !! id=%s の施設オブジェクト範囲を特定できません" % vid); continue
        seg = s[st:en]
        mo = re.search(r'"ota":\s*\{', seg)
        if not mo:
            print("    !! ota が見つかりません"); continue
        oe = json_obj_end(seg, mo.end() - 1)
        ota = seg[mo.end() - 1:oe]
        # 前後どちらかのカンマごと落とす。最後の1件なら ota 自体を空にする。
        mk = re.search(r'(,\s*)?"%s":\s*"[^"]*"(\s*,)?' % re.escape(k), ota)
        if not mk:
            print("    !! ota に %s がありません" % k); continue
        rep = ota[:mk.start()] + ("," if mk.group(1) and mk.group(2) else "") + ota[mk.end():]
        print("    ota から %s を削除" % k)
        s = s[:st] + seg[:mo.end() - 1] + rep + seg[oe:] + s[en:]

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
            # ota のリンクはボタンのラベルで対象を特定する（OTA_LABEL の説明を参照）。
            if k in OTA_LABEL:
                label = OTA_LABEL[k]
                pat = (r'(<a class="ota-btn"[^>]*href=")([^"]*)("[^>]*>%s<span>)'
                       % re.escape(label))
                m = re.search(pat, s)
                if not m:
                    print("    !! 個別ページに「%s」のボタンがありません" % label)
                    continue
                cur = old_vals.get(k)
                if cur is not None and m.group(2) != esc(cur):
                    print("    !! 「%s」ボタンの href が index.html と一致しません" % label)
                    continue
                s = s[:m.start(2)] + esc(val) + s[m.end(2):]
                print("    個別ページの「%s」ボタンを差し替え" % label)
                continue
            # fact 行ではないが本文中にそのまま出る項目（official / addr など）。
            # 値の直後が **閉じ引用符かタグの始まり** であることまで確かめる。
            # 引用符だけを見ていると、テキストノードに出る値を取りこぼす
            # （addr は <div class="modal-addr">住所<a href=...> の形で出る）。
            # 前方一致での巻き添えは、URL の続きが " でも < でもないので防げる。
            if k not in VILLA_FACTS:
                old = old_vals.get(k)
                if old:
                    pat = re.escape(esc(old)) + r'(?=["<])'
                    n = len(re.findall(pat, s))
                    if n:
                        s = re.sub(pat, esc(val).replace("\\", "\\\\"), s)
                        print("    %s を %d 箇所差し替え -> %s" % (k, n, val))
                    # 「大きな地図で見る」の href と modal-map の iframe は、施設名と
                    # 住所を percent-encode して query に載せている。平文の置換では
                    # 当たらないので符号化した形でも置き換える。**これが無いと本文と
                    # JSON-LD だけ新住所になり、地図リンクだけ旧住所を指したまま残る。**
                    # 2026-09 に16施設32URLが実際にその状態だった。id=239 は姉妹施設の
                    # 住所を、id=132/133 は入れ替わった住所を地図が指し続けていた。
                    enc = urllib.parse.quote(old)
                    if enc != old and enc in s:
                        n2 = s.count(enc)
                        s = s.replace(enc, urllib.parse.quote(val))
                        print("    %s の地図リンクを %d 箇所差し替え" % (k, n2))
                continue
            label, fmt = VILLA_FACTS[k]
            new = fmt % val
            s2 = re.sub(r'(<span class="fact-label">%s</span>'
                        r'<span class="fact-val">)[^<]*(</span>)' % re.escape(label),
                        lambda m: m.group(1) + new + m.group(2), s, count=1)
            if s2 != s:
                print("    fact「%s」を %s に更新" % (label, new))
                s = s2

        # index.html から消した ota キーは、個別ページのボタンも消す。
        # これが無いと利用者には壊れたリンクが見えたままになる。
        for k in (fx.get("remove_ota") or []):
            label = OTA_LABEL.get(k)
            if not label:
                continue
            pat = (r'<a class="ota-btn"[^>]*>%s<span>[^<]*</span></a>'
                   % re.escape(label))
            s2 = re.sub(pat, "", s, count=1)
            if s2 == s:
                print("    !! 個別ページに「%s」のボタンがありません" % label)
            else:
                print("    個別ページから「%s」ボタンを削除" % label)
                s = s2

        # add_tags は pill も足す。既存 pill と同じ書式に合わせるため、
        # 他ページから同じラベルの pill をひな型として拾う。
        for t in fx.get("add_tags", []):
            label = {"sauna": "サウナ", "pet": "ペットOK", "bbq": "BBQ",
                     "onsen": "温泉", "pool": "プール"}.get(t)
            if not label or ('>%s</span>' % label) in s:
                continue
            tmpl = None
            for q in glob.glob("villas/*.html"):
                m = re.search(r'<span class="pill" style="[^"]*">%s</span>' % label,
                              io.open(q, encoding="utf-8").read())
                if m:
                    tmpl = m.group(0); break
            if not tmpl:
                print("    !! pill「%s」のひな型が見つかりません" % label); continue
            m2 = re.search(r'(<span class="pill"[^>]*>[^<]*</span>)', s)
            if m2:
                s = s[:m2.end()] + tmpl + s[m2.end():]
                print("    pill「%s」を追加" % label)

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

    # **削除は一次記録からも消さないと、次のマージで蘇る。**
    # merge_desk.py は「spec-data.js に無い項目」を追加するので、
    # data/desk-research.js に古い記録が残っていると削除が無かったことになる。
    # 2026-09 に id=131 の kids_free を削除した直後のマージで実際に復活した。
    if fx.get("remove_spec"):
        rp = "data/desk-research.js"
        rs = ro = io.open(rp, encoding="utf-8").read()
        hit = []
        for k in fx["remove_spec"]:
            pat = r'(^  "%s": \{(?:[^{}]|\{[^{}]*\})*?\n  \},?)' % vid
            for mm in list(re.finditer(pat, rs, re.M | re.S)):
                blk2 = mm.group(1)
                nb2 = re.sub(r"\n    %s:\s*\{[^}]*\},?" % re.escape(k), "", blk2)
                nb2 = re.sub(r",(\s*\n  \},)", r"\1", nb2)
                if nb2 != blk2:
                    rs = rs.replace(blk2, nb2, 1)
                    hit.append(k)
        if hit:
            write(rp, rs, ro)
            print("    一次記録からも削除: %s（マージでの復活を防ぐ）"
                  % ", ".join(sorted(set(hit))))

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
