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
    "8": {"name": "&SUN Laie back",
            "reason": "ROOMページ ROOFTOP「サマーベッド×2／テーブルセット×1」→outdoor_rest=yes。**kitchen_type は入れない**: ROOMページ「3口IHキッチン」とFAQページ「ガスコロン（3口）」がサイト内で食い違う。同じ「3口」なのに IH とガスで矛盾しており判断できない（CLAUDE.md記載のサイト内食い違い類型）。なお公式の住所表記は「久枝1274-7」でDBの「1274-3」と番地末尾が異なるが、施設名・写真・特徴が一致し南房総である点も確認済み（2026-08確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/andsun-laie-back/"}}},

    "62": {"name": "RICKA KATSUURA",
            "reason": "一休の設備欄「✕ ペット可」＋基本情報「不可。ペットのお持ち込みは、施設の衛生管理上、固くお断りいたします。」→pet_ok=no（一休内で矛盾なく明確な否定）。coldbath=bath は既存値のままとするが、公式トップ「チラーで冷やされた水風呂」に対しRoomページは「サウナで温まった後、プールで心地よくクールダウンする」とも書いており pool 兼用の余地がある（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052124/"}}},

    "65": {"name": "THE NALU",
            "reason": "一休「Wi-Fi 利用可能」。**coldbath は入れない**: POOLページのプールは「8m×4mのゆったりとした温水プール」と温水仕様が明記されており水風呂兼用とは考えにくいが、水風呂が無いという否定表現でもないため未調査に戻す。サウナ専用ページは「完全プライベートなサウナも完備。自分だけのリズムで心身を整える極上のひとときを。」と形容詞のみで仕様が無い（CLAUDE.md の「外れ」の型そのもの）（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052209/"}}},

    "70": {"name": "The Pacific Retreat TATEYAMA",
            "reason": "FAQ「無料でご利用頂けます」（Wi-Fi）。他項目は既存値と一致。sauna_type / stove は「本格的なサウナ」としか書かれておらず構造・熱源の記載が無い（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://pacific-retreat-tateyama.com/faq/"}}},

    "71": {"name": "Casita Laguna",
            "reason": "WebFetchが403のため実機ブラウザで閲覧。ABOUTページ諸元表「【サウナハウス】3～4人 サウナヒーター（ハルビア電気式）、水風呂」→stove=electric、「【キッチン】IHコンロ、炊飯器…」→kitchen_type=ih、「【その他】…Wi-Fi（無料）」。pet_ok=no は一休「✕ ペット可」「不可」（公式に記載なし）。coldbath=bath はFAQ「プールはありますか？いいえ…3m×1.2mと広めの水風呂がございます」でプールを明示的に否定したうえでの水風呂。**sauna_type は入れない**: 「サウナ棟」「サウナハウス」の呼称は hut を思わせるが、バスルームから専用ドアで内部接続しており indoor とも読める（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://casitalaguna.com/faq"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-08",
                                        "url": "https://casitalaguna.com/faq"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://casitalaguna.com/faq"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://casitalaguna.com/faq"}}},

    "73": {"name": "SANU 2nd Home 南アルプス1st",
            "reason": "同上のMOSS型記事に南アルプス1stが名指しされている。「ロウリュ用バケツ/柄杓」→loyly=yes、「テラスに水風呂とととのい椅子を備えています。」→coldbath=bath / outdoor_rest=yes。wifi は一休。pet_ok=yes は既存値のままとするが、一休が設備欄「✕ ペット可」・基本情報「可（愛犬と泊まれる部屋に限定）」と自己矛盾しており確度中（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"}}},

    "74": {"name": "SANU 2nd Home 八ヶ岳2nd",
            "reason": "一休「Wi-Fi 利用可能」。他項目は既存値と一致し、とくに sauna_type=barrel は公式マガジン「SANU CABIN BEE with Sauna」の「ONE SAUNAのバレルサウナを採用」（対象拠点に八ヶ岳2ndを明記）で独立に裏付けられた（2026-08確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052019/"}}},

    "75": {"name": "SANU 2nd Home 八ヶ岳3rd",
            "reason": "同上のMOSS型記事に八ヶ岳3rdが名指しされている。「ロウリュ用バケツ/柄杓」→loyly=yes、「オープンエアの外気浴で心地よいひと時を」→outdoor_rest=yes。wifi は一休。sauna_exists=room は公式拠点ページの部屋タイプ一覧に加え、SANUのプレスリリース「プライベートサウナ：3棟 ＊プライベートサウナは一部の棟のみ対象となります」でも裏付けられた（既存値と一致）（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"}}},

    "76": {"name": "SANU 2nd Home 河口湖2nd",
            "reason": "SANU公式マガジン「SANU CABIN MOSS with Sauna」記事。対象拠点として河口湖2nd・八ヶ岳3rd・南アルプス1stを名指ししている（ブランド一律適用ではなく拠点の列挙）。「ロウリュ用バケツ/柄杓」→loyly=yes、「テラスに水風呂とととのい椅子を備えています。」→coldbath=bath / outdoor_rest=yes、「バルコニーにはゆったりと寛げるチェアが備えられ」。wifi は一休。**sauna_type / stove は入れない**: MOSS型の構造・熱源は記載がない。BEE型（八ヶ岳2nd）の同種記事にはバレルと明記があるが、型が違うので流用しない。なお同記事は水風呂が冬季11〜4月は凍結のため利用制限とも書いており、季節制限を記録する項目が無い（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"}}},

    "81": {"name": "古民家宿るうふ　織之家",
            "reason": "公式「ロウリュでじっくり汗をかくフィンランドサウナで心身をスッキリ流し」→loyly=yes。一休「✕ ペット可」「ペット 不可」、一休「Wi-Fi 利用可能」。**stove は入れない**: 「フィンランドサウナ」はスタイルの呼称で熱源ではない。備品欄の「ペレットストーブ、灯油ストーブ」は居室の暖房でサウナのストーブとは別物（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/shikinoie/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/shikinoie/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/shikinoie/"}}},

    "82": {"name": "古民家宿るうふ　祝之家",
            "reason": "公式「ロウリュでじっくり汗を引き出し、水風呂でリセット、貸切サウナをご堪能。」→loyly=yes。一休の設備欄「✕ ペット可」「ペット 不可」→pet_ok=no、一休「wi-fiが利用可能です」。sauna_type は「杉のサウナ」と材質のみ、stove は熱源の記載が無いため入れない（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/iwainoie/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/iwainoie/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://loof-inn.com/hotels/iwainoie/"}}},

    "92": {"name": "VILLA SAISON FUJI",
            "reason": "公式「アイランドキッチンのIHコンロに加え、室内でもBBQをお楽しみ頂けるように、ブロイル・キングのBBQガスグリルを備えつけました」→kitchen_type=both、公式トップ「サウナとデイベッドで整いましょう」→outdoor_rest=yes。sauna_type は「八角推で、全面ガラス張りの構造」でプールデッキ設置の独立建屋だが indoor / hut のどちらとも決めがたく入れない（2026-08確認）",
            "set_spec": {
                         "kitchen_type": {"v": "both", "src": "desk", "at": "2026-08",
                                        "url": "https://villa-saison-fuji.com/villa/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://villa-saison-fuji.com/villa/"}}},
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
