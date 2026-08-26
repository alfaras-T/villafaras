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
    "9": {"name": "sendouQ",
            "reason": "公式施設紹介「火を使わないので安全に使用できる電気式のサウナです。大人3人がゆったりと入れる広さで、宿泊中お好きな時間にご利用いただけます。サウナ浴の後、隣接のプールで汗を流す爽快感は格別です。」「※ストーブの水かけはご遠慮ください。電気式サウナ窯の為漏電の恐れがあります。」——1段落から5項目が確定した。ロウリュは明示的に禁止されており理由（漏電）も書かれているため、**本DBで初の loyly=no**。クールダウンは隣接プールなので coldbath=pool（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://sendouq.jp/about/?facility=1st"},
                         "sauna_cap": {"v": 3, "src": "desk", "at": "2026-08",
                                         "url": "https://sendouq.jp/about/?facility=1st"},
                         "sauna_hours": {"v": "h24", "src": "desk", "at": "2026-08",
                                           "url": "https://sendouq.jp/about/?facility=1st"},
                         "loyly": {"v": "no", "src": "desk", "at": "2026-08",
                                     "url": "https://sendouq.jp/about/?facility=1st"},
                         "coldbath": {"v": "pool", "src": "desk", "at": "2026-08",
                                        "url": "https://sendouq.jp/about/?facility=1st"}}},

    "11": {"name": "Avalon Cove",
            "reason": "登録URL（terracecollections.jp）の個別ページは404で、実質の一次情報は一休。「エストニア製のHUUMサウナ」→HUUMは電気ヒーターブランドのため stove=electric、「ペット 不可」「wi-fiが利用可能です」（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                     "url": "https://www.ikyu.com/00052130/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ikyu.com/00052130/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.ikyu.com/00052130/"}}},

    "23": {"name": "The TRAVELERS Chateau Tateyama",
            "reason": "公式（yamato-stay.com）はJS描画で本文取得不可。一休英語版に「barrel sauna」「Entire house rental (3LDK) for up to 10 guests」「Free internet (Wi-Fi)」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                          "url": "https://www.ikyu.com/en-us/00051783/11509093/10260125/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://www.ikyu.com/en-us/00051783/11509093/10260125/"}}},

    "25": {"name": "THE POOL HOUSE TOKYO BAY",
            "reason": "公式FAQ「TOKYO BAYの宿泊者のみご利用可。（22：00～8：00までの間はご使用いただけません。）」→sauna_hours=limited、「ペット同伴は、宿泊・日帰り・撮影ともご遠慮いただいております」、「館内、Wi-Fi完備です」。姉妹施設「木更津」はミストサウナ・定員8名で仕様が異なるため除外した（2026-08確認）",
            "set_spec": {
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://thepoolhouse.jp/faq"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://thepoolhouse.jp/faq"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://thepoolhouse.jp/faq"}}},

    "66": {"name": "Villa Yno",
            "reason": "公式サイトが存在しないためOTAを出典とする。「ペット：不可」「wi-fiが利用可能です」。なお同ページ内に「定員 1名～9名」（OTA仕様上限）と「10名まで宿泊可能」が併存しており、後者を採る既存値10が正しい（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://travel.yahoo.co.jp/00052212/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://travel.yahoo.co.jp/00052212/"}}},

    "86": {"name": "hotel norm. air",
            "reason": "公式「温度は95℃で設定されており」「4〜5人でお楽しみいただけます」→sauna_temp=95, sauna_cap=5（範囲は上限）。一休の滞在記に「日本のホテル初導入のイタリア製」「ユニークな形をした大きなバスタブ」→coldbath=tub、「IHヒーターにはコンロが3つ」、「バルコニーには外気浴用の椅子があり」。酷似名の別施設 hotel norm. fuji（hotel-norm.com）の「85℃サウナ・10℃水風呂」と混同しないよう区別した（2026-08確認）",
            "set_spec": {
                         "sauna_temp": {"v": 95, "src": "desk", "at": "2026-08",
                                          "url": "https://www.hotel-normair.com"},
                         "sauna_cap": {"v": 5, "src": "desk", "at": "2026-08",
                                         "url": "https://www.hotel-normair.com"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://www.hotel-normair.com"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://www.hotel-normair.com"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://www.hotel-normair.com"},
                         "rest_chair": {"v": "chair", "src": "desk", "at": "2026-08",
                                          "url": "https://www.hotel-normair.com"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://www.hotel-normair.com"}}},

    "87": {"name": "hotel norm. ao",
            "reason": "公式「湧水風呂とスチームサウナ」、楽天トラベル記事「富士山の伏流水が使われ」→water_src=spring（2ソース一致）。サウナはスチーム式で sauna_type の4区分（indoor/hut/barrel/tent）に当てはめられないため入れない（2026-08確認）",
            "set_spec": {
                         "water_src": {"v": "spring", "src": "desk", "at": "2026-08",
                                         "url": "https://www.hotel-normao.com"}}},

    "96": {"name": "yl&Co.Hotel in Mt.Fuji",
            "reason": "公式FAQ「申し訳ございません。ペット同伴でのご宿泊はご遠慮させていただいております。」（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                      "url": "https://www.ylandco-hotel.com/faq.html"}}},

    "97": {"name": "VILLA　SUOMI",
            "reason": "公式「サウナストーンにアロマ水を掛けて、湿度と香りでじっくりと発汗させていく」「セルフで楽しめる」→loyly=yes、「バスタブに水を張れば、併設したサウナ用の水風呂としても」→coldbath=tub、「テラスでくつろげるように折り畳み式のチェアーをご用意」→outdoor_rest=yes, rest_chair=chair。サウナ温度はトップ「６０℃～８０℃程度」とfixtures「７０℃～８０℃ぐらい」で下限が食い違うが上限は一致するため80を採る（2026-08確認）",
            "set_spec": {
                         "sauna_temp": {"v": 80, "src": "desk", "at": "2026-08",
                                          "url": "https://villa-suomi.jp/fixtures/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://villa-suomi.jp/fixtures/"},
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://villa-suomi.jp/fixtures/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://villa-suomi.jp/fixtures/"},
                         "rest_chair": {"v": "chair", "src": "desk", "at": "2026-08",
                                          "url": "https://villa-suomi.jp/fixtures/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://villa-suomi.jp/fixtures/"}}},

    "98": {"name": "SILVER SPRAY 山中湖",
            "reason": "既存の sauna_exists=shared（日帰りサウナコースあり）と整合する。テントサウナで薪ストーブ、サウナ室の収容人数は10名（宿泊定員10名とは別項目）。準備に1時間30分を要し利用時間枠が決まっているため sauna_hours=reserve。「富士山を眺めながら外気浴」（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                          "url": "https://silver-spray.jp/main.php"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                     "url": "https://silver-spray.jp/main.php"},
                         "sauna_cap": {"v": 10, "src": "desk", "at": "2026-08",
                                         "url": "https://silver-spray.jp/main.php"},
                         "sauna_hours": {"v": "reserve", "src": "desk", "at": "2026-08",
                                           "url": "https://silver-spray.jp/main.php"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                            "url": "https://silver-spray.jp/main.php"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                     "url": "https://silver-spray.jp/main.php"}}},

    "105": {"name": "BLANC FUJI",
            "reason": "公式FAQ「チェックイン当日は24時まで、チェックアウト日は7時から10時まで」→sauna_hours=limited、「全室でWi-Fiインターネットを無料でご利用頂けます」。施設ページに「サウナーに大人気のインフィニティチェアを完備」。既存の sauna_exists=room は正しく、加えて「Suite Pet Villa -Sauna-」（犬同伴可・サウナ付き）という客室タイプが別途あることが判明したため pet_ok は単一値に決められず入れない（2026-08確認）",
            "set_spec": {
                         "sauna_hours": {"v": "limited", "src": "desk", "at": "2026-08",
                                           "url": "https://blan-c.com/fuji/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                    "url": "https://blan-c.com/fuji/faq/"},
                         "rest_chair": {"v": "infinity", "src": "desk", "at": "2026-08",
                                          "url": "https://blan-c.com/fuji/faq/"}}},

    "252": {"name": "伊豆高原テントリゾート",
            "reason": "公式お知らせ「大好評だったテントサウナが、最新設備と薪ストーブでグレードアップして帰ってきました！」→sauna_type=tent, stove=wood。stay.php のヴィラサイト設備欄に「キッチン（IH）」。guide.php「ヴィラサイトはペット同伴OK。（テントサイトはプランによりOK。キャビンはご遠慮いただいております）」。capacity は stay.php のヴィラサイト欄が「定員 5名」で既存値6と食い違うが、宿泊タイプが複数ありDBの1件がどれを指すか特定できないため変更しない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-08",
                                          "url": "https://tentresort-izu.com/stay.php"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                     "url": "https://tentresort-izu.com/stay.php"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                            "url": "https://tentresort-izu.com/stay.php"}}},
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

print("\n完了%s" % ("（dry-run。実際には書き換えていません）" if DRY else ""))
