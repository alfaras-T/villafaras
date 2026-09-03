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
    "59": {"name": "Under the Sea UBARA",
            "reason": "一休のプラン本文「＜一棟貸し切り＞ご宿泊プラン※最大6名様まで」→capacity=6（部屋種別欄の「定員1名～6名」ではなくプラン本文の施設固有の記述を採った）。pet_ok=yes は公式FAQ「基本的には2匹まで同伴可能です。わんちゃん同伴オプションをご選択ください。※3匹以上の頭数、大型犬要相談」＋一休「ペット 可 小型から中型２匹まで６６００円（税込）」の2ソース。住所「千葉県勝浦市鵜原759-23」は公式・一休とも完全一致（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052044/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052044/"}}},

    "67": {"name": "EKVOLI MARINA VILLA, Isumi Garden",
            "reason": "**公式サイト本体にはサウナ形式の記載が無く、運営会社のクラウドファンディングページで確定した。** 「ウッドデッキから広がる5＊10mの大型プール × 檜の露天風呂 × **薪ストーブのバレルサウナ**。檜の露天風呂に浸かり、薪で焚いた熱々のバレルサウナで汗をかき」→sauna_type=barrel（**サウナ自体を修飾しており熱源も同時に確定できる書き方**。既存の stove=wood とも整合）。サウナイキタイの「ドライサウナ 対流式（ストーン） 薪」とも一致。pet_ok=yes は一休「ペット可」「1匹につき11,000円の追加料金」（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.makuake.com/project/ekvoli/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.makuake.com/project/ekvoli/"}}},

    "73": {"name": "SANU 2nd Home 南アルプス1st",
            "reason": "SANU公式の拠点別ページ「定員 4名 セミダブル2台 追加寝具1セット」＋拠点一覧カード「南アルプス1st／MOSS／4名／サウナ・ドッグフレンドリー」→capacity=4（一休の「1名～4名」はOTA範囲表記なので不採用）。pet_ok=yes は同ページ「ドッグフレンドリー」＋一休。**MOSS型サウナ記事の対象拠点に「南アルプス1st」が名指しされていることも再確認**した（誤流用ではない）（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/minami-alps/sites/minami-alps1st"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/minami-alps/sites/minami-alps1st"}}},

    "76": {"name": "SANU 2nd Home 河口湖2nd",
            "reason": "SANU公式の拠点別ページ「定員 4名 セミダブル2台 追加寝具1セット」→capacity=4、「ドッグフレンドリー」複数表記→pet_ok=yes。**MOSS型サウナ記事の対象拠点に「河口湖2nd」が名指しされていることも再確認**した（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/kawaguchiko/sites/kawaguchiko2nd"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/kawaguchiko/sites/kawaguchiko2nd"}}},

    "91": {"name": "ビジョングランピングリゾート山中湖",
            "reason": "**capacity を 6 から 8 に訂正する。** 公式の客室タイプ別ページに「デラックススタイル（6mドームテント）定員：1〜6名」「ウィズドッグスタイル（6mドームテント）定員：1〜6名」「**スイートスタイル（8mドームテント）定員：2〜8名**」と3種の定員が明記されている。既存の6はデラックス／ウィズドッグの数字で、スイート型（最大8名）を代表していない。全15棟で「全棟利用時は最大N名」の記載は無いが、**id=113 ASH Villa（10名/6名→10）、id=38 Asile＆OLILI（10名/14名→14）、id=117 THE SECOND（14名/6名→14）、id=238 月と太陽（5/6/10/10→10）と同じく施設全体の最大を採る。** pet_ok=yes は公式のペット専用ページ「ご宿泊いただけるワンちゃんは体重が40キロまでのワンちゃんです」「大型犬：1頭まで 小型～中型犬：2頭まで」。**outdoor_rest=yes を新規記録**（公式「外気浴用の椅子にはインフィニティチェアをご用意」）（2026-09確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://vision-glamping.com/yamanakako/stay"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://vision-glamping.com/yamanakako/stay"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://vision-glamping.com/yamanakako/stay"}}},

    "95": {"name": "天空の温泉ヴィラ紬 河口湖",
            "reason": "**capacity を 4 から 6 に訂正する。** 公式の客室ページに棟タイプ別の最大人数が明記されている。「スイートヴィラタイプ：最大**6**名様」「スタンダードヴィラタイプ：最大4名様」「グランピングタイプ：最大4名様」。既存の4はスイートヴィラを代表していない。id=91 と同じく施設全体の最大を採る。**coldbath=bath と outdoor_rest=yes を新規記録**（公式 /spa/「水風呂と外気浴コーナーで心身ともにリフレッシュできる至福のひとときをお過ごしください。」。プール・浴槽兼用の記載は無く単独の水風呂）。**kitchen_type は本波の直前に gas から cassette に訂正済み**（「室内にガスボンベ式のカセットガスコンロを用意」）（2026-09確認）",
            "set_villa": {"capacity": "6"},
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/tsumugi/room/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/tsumugi/room/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/tsumugi/room/"}}},

    "101": {"name": "KURA YARD",
            "reason": "公式サウナページ「…セルフロウリュが可能。」→loyly=yes。**stove=electric は別途交差検証に回した**: 「サウナストーブは、本場フィンランドのサウナメーカーHarviaの『LEGEND15』を採用しており」と型番が明記されているが、**Harvia の Legend シリーズは一般に薪式として知られている**ため、型番から電気式と断定してよいか確認が要る（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://kurayard.com/sauna"}}},

    "107": {"name": "ReTune | SPA & SAUNA / VILLA",
            "reason": "公式FAQの質問文自体に「**テントサウナ**のデッキに椅子はいくつありますか？」とあり回答が「デッキには４脚ご用意がございます」→sauna_type=tent。pet_ok=yes は同FAQ「小型中型犬は2匹まで。大型犬は1匹までご一緒にお過ごしいただけます。」。既存の capacity=10 も同FAQ「10名までご宿泊が可能ですが、ゆったりご利用されたい場合は7名を推奨」と整合（**推奨7名は comfort_cap に相当する情報**）（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-09",
                                        "url": "https://retune.jp/retune_faq"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://retune.jp/retune_faq"}}},

    "108": {"name": "THE THIRD PLACE Mt.Fuji",
            "reason": "一休「1日1組限定でご利用いただけるバレルサウナ」→sauna_type=barrel。**pet_ok=no を新規記録**（一休「ペット 不可」）。**capacity=6 は変更しない**: 予約サイト（chillnn）に棟別で「煌–Köu–（1st棟）最大4名」「燈–Töu–（2nd棟）最大6名」「燿–Yöu–（3rd棟）最大6名」とあり、6が1st棟を代表していないと指摘されたが、**施設全体の最大は6なので既存値のままでよい**（最大を採る方針）（2026-09確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052393/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052393/"}}},

    "110": {"name": "THE BLISS FUJI",
            "reason": "一休「最大8名が泊まれる完全プライベート」→capacity=8（部屋種別欄の「定員1名～8名」だけでなく紹介文にも施設固有の数字がある）。pet_ok=yes は一休「小型犬、中型犬を合計2匹までお連れいただけます。愛犬同伴料は…1滞在につき一律8,500円です。」。**stove / loyly / kitchen_type は未確認のまま**: 公式 hotel.alterna3.jp がJS描画で本文を取得できず、一休にも記載が無い（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052516/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052516/"}}},

    "113": {"name": "ASH Villa 富士河口湖",
            "reason": "**stove=electric と loyly=yes を新規記録する。公式FAQが一問一答で両方を確定させている。** 「Q. ストーブを付ける方法など利用方法はどんな感じですか？ A. **電気ストーブ**になりますのでスイッチにて簡単にご使用いただけます。」「Q. ロウリュはできますか？ A. はい。電気ストーブ上部のサウナストーンにアロマオイルと一緒にお楽しみください。」。**coldbath は別途交差検証に回した**: 公式ステイページの「お風呂は大きなヒノキ風呂…サウナのあとの水風呂にもご利用いただけます。」を根拠に bath から tub への訂正が提案されたが、これは Deluxe Villa 1010 の記述で、もう一方の 2-Bedroom Villa 2020 の水風呂が確認できていない。**sauna_type=barrel は不明のまま**: 公式は「HARVIA製ストーブを備えたプライベートサウナ」までで形状の記載が無い（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://ash-villa.com/faq/"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://ash-villa.com/faq/"}}},

    "114": {"name": "エンゼルフォレスト那須",
            "reason": "**capacity を 6 から 10 に訂正する。** 公式の客室ページに8タイプすべての定員が明記されている。「カミーナ4名タイプ：定員4名」「貸別荘1541：定員5名」「ノッカ：定員6名」「貸別荘フィーカ：定員6名」「カミーナ6名タイプ：定員6名」「ルンド：定員8名」「ルオント：定員8名」「**グランノッカ：定員10名**」。既存の6は8タイプ中3タイプの数字にすぎない。施設全体の最大を採る方針に従う。sauna_exists=room は、共用温泉（「和風呂・洋風呂共に内湯、サウナ、露天風呂がございます」）とは別に**客室内サウナがあるのは「ルンド」「フィーカ」の2タイプのみ**と確認できたので妥当。**stove は入れない**: ルンドの説明にある「薪ストーブ・温泉・サウナ・インナーテラス・半露天風呂つき」は設備の並列列挙で、サウナ自体を修飾していない（2026-09確認）",
            "set_villa": {"capacity": "10"},
            "set_spec": {
                         "capacity": {"v": 10, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ang-ns.com/stay/"},
                         "sauna_exists": {"v": "room", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ang-ns.com/stay/"}}},

    "119": {"name": "SANU 2nd Home 那須2nd",
            "reason": "SANU公式の拠点別ページ「定員 4名 セミダブル2台 ※大人2名まで推奨」→capacity=4（建築タイプは「独立型キャビン『BEE』5棟」と確認）。pet_ok=yes は同ページの「サウナ／ドッグフレンドリー」室内タイプ。**BEE型サウナ記事の対象拠点に「那須2nd」が名指しされていることも再確認**し、既存の sauna_type=barrel の出典が妥当と裏付けられた。**stove は不明のまま**: 記事にも ONE SAUNA の製品ページにも熱源の明記が無い（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/nasu/sites/nasu2nd"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.sa-nu.com/areas/nasu/sites/nasu2nd"}}},
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
