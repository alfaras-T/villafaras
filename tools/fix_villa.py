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
    "90": {"name": "totonoco 湖畔の隠れ家",
            "reason": "出典の無かった3項目に裏付けが取れた。公式「サウナ、水風呂、外気浴コーナーで『整う』時間をぜひお過ごしください」→coldbath=bath / outdoor_rest=yes、施設概要「インターネット環境: フリーWi-Fi」→wifi=yes。**kitchen_type は入れない**: 設備欄は「調理器具・食器類」のみでコンロ自体の記載が無い（2026-09確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/totonoco/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/totonoco/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/totonoco/"}}},

    "94": {"name": "abrAsus hotel Fuji",
            "reason": "公式デザインページ「窓のないオープンリビングで…サウナのあとの外気浴にもぴったりです」→outdoor_rest=yes（**サウナと明示的に紐付いている**）。FAQ「外にあるテラスは、寒くないですか？→テラスのソファに電気毛布2枚のご用意がございます」も補強。**sauna_type は入れない**: 公式は「SAUNA TRAILER」＝トレーラーサウナで、indoor/hut/barrel/tent のどれにも該当しない（スキーマ不足の新しい型）。**wifi も入れない**: FAQ全項目（約60問）をDOM直読みで確認したが一切言及が無い（2026-09確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://abrasushotel.jp/fuji/room1/"}}},

    "97": {"name": "VILLA　SUOMI",
            "reason": "一休の設備欄「✕ペット可」＋基本情報「不可」で一致。既存の capacity=6 も「クンプラ 定員1名〜6名」「ワロイサ 定員1名〜6名」と2室型とも独立に6を示しており、9名上限の機械読み取りではない。**sauna_type は入れない**: 「フィンランドのHONKAのログホームだからこそ、本場のフィンランドサウナを」から indoor が推測できるが「フィンランドサウナ」はスタイル呼称。**stove も入れない**: 設備リストは「sauna stove」と英語表記のみ。なお**BBQ用の「Soloストーブ」（焚き火台）が別項目で存在する**ので混同しないこと（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051019/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051019/"}}},

    "115": {"name": "有形文化財ホテル 飯塚邸",
            "reason": "公式の客室ページ6室（本宅／新宅A／新宅B／文庫蔵／土蔵A／土蔵B）すべての設備欄に「ＩＨ」「Wifi」「ペット不可」が明記されており、一休の設備欄「✕ペット可」＋基本情報「不可」とも一致する。**capacity=3 は要検討**: 本宅4名・新宅A5名・新宅B5名・文庫蔵3名・土蔵A3名・土蔵B3名と棟ごとに異なり、「最大4〜5名様×3グループ様まで」という記述はあるが全棟合計の単一数値が無い。既存の3は最小値のみを反映している。**住所の不一致を発見**: DBは「栃木県那須郡那珂川町矢又1948」だが、公式のフッター・アクセス欄と一休がどちらも「栃木県那珂川町馬頭360」。**チャネルAの標高・所要時間は住所から導出しているので、住所が誤っていれば連鎖する**（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://iizukatei.ohtawaragt.co.jp/rooms"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://iizukatei.ohtawaragt.co.jp/rooms"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://iizukatei.ohtawaragt.co.jp/rooms"}}},

    "129": {"name": "和モダングランピング｜NAGOMI CAMP",
            "reason": "グランピング4室（籠・麻・波・紗綾）すべての設備欄に「無料Wi-Fi」。既存の sauna_type=barrel も専用サウナページの「バレルサウナ／BARREL SAUNA／森林サウナ」で裏付けが取れた。**kitchen_type は入れない**: facility / glamping ページとも「ある物だけを列挙する」形式（フロント・トイレ・シャワー・BBQ・ドリンクバー等）で、不記載を否定の根拠にできない（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.nagomi-camp.jp/glamping"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.nagomi-camp.jp/glamping"}}},

    "137": {"name": "P's Wood 箱根仙石原",
            "reason": "**同一ブランドに伊豆高原・元箱根の別施設があるため /hakone/ ページのみを参照した。**「国産檜のサウナは4名が同時にご利用できますので、何度でも汗を流してください。ロウリュも可能です。」→loyly=yes、設備＜キッチン＞欄「IHコンロ」「IHクッキングヒーター」→kitchen_type=ih。既存の capacity=12 も「12名まで宿泊OK」がトップ文章と概要表の2箇所にあり裏付け。**stove は入れない**: 「国産檜のサウナ」「檜の香り」は**建材の説明であって熱源ではない**。**outdoor_rest も入れない**: ウッドデッキはBBQ専用と明記されている（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://ps-wood.jp/hakone/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://ps-wood.jp/hakone/"},
                         "capacity": {"v": 12, "src": "desk", "at": "2026-09",
                                        "url": "https://ps-wood.jp/hakone/"}}},

    "149": {"name": "MOROISOSO-サウナ＆温水プール付きラグジュアリーヴィラ",
            "reason": "**stove がサウナの説明文中に直接書かれている数少ない例。** 「サウナストーブは、薪を使用する本格フィンランド式です。ストーンにゆっくりと水をかけることで、ロウリュも楽しめます。」→stove=wood / loyly=yes。「水風呂、温水プール、サウナチェアをご用意しています」→coldbath=bath（水風呂と温水プールが別項目）／outdoor_rest=yes。sauna_exists は「Sauna 絶景の中で、最高の『ととのい』体験を。」、pet_ok=yes は公式「with Dogs」＋一休「○ペット可」＋基本情報「可」の三重確認。**sauna_type は入れない**: 間取り図で「Ground（庭）」区分にサウナ・プール・ドッグラン・BBQが分類され母屋と別区画とは分かるが、小屋／バレル／テントの形状記載が無い（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://moroisoso.jp/facility"}}},

    "154": {"name": "LULLA",
            "reason": "既存の sauna_exists=yes（一休「サウナ：あり」）と capacity=4（一休「定員 1名～4名」。9名上限の機械読み取りではない）に出典を付ける。**outdoor_rest は入れない**: 「屋上」がお部屋情報にあるがサウナとの関連付けが明示されていない（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052476/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052476/"}}},

    "165": {"name": "箱根懐來",
            "reason": "公式「檜の香りが心地よいプライベートサウナではロウリュも堪能できます」→loyly=yes。**kitchen_type=none をこの項目で2件目として記録する**: 「安全管理の観点から、火器の使用や食材の持ち込みによる調理はご遠慮いただいております」という**明示的な禁止文**があり、「システムキッチン」の表記はあるが実際は調理不可。**sauna_type は入れない**: 「サウナのすぐ側に水風呂を備え、そのままオープンテラス/内風呂/温泉露天風呂も回遊できます」から屋内の導線と読めるが「室内」の直接表記が無い。**stove も入れない**: 温度35〜110℃・1℃刻み・5名収容と詳細な記述があるのに熱源だけ書かれていない（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.hakone-kairai.jp"},
                         "kitchen_type": {"v": "none", "src": "desk", "at": "2026-09",
                                        "url": "https://www.hakone-kairai.jp"}}},

    "190": {"name": "Hygge chalet hakuba（ヒュッゲ シャレー）",
            "reason": "一休の設備欄「✕ペット可」＋基本情報「不可」で一致。**サウナの改装履歴が判明した**: 2021.02.14 のニュースは「MORZH SKY(テントサウナ)を導入しました」だが、2024年春に「本格薪ストーブ式アウトドアサウナ」へ更新されており、現行の /system/ ページにテントの語は一度も出てこない。既存の stove=wood（2026-08・出典あり）はこの2024年の記述と整合する。**sauna_type は入れない**: 「アウトドアサウナ」では小屋かバレルかを区別できない。**季節制限（スキーマ外）**: 「（※冬季は凍結のため利用不可）」が /system/ ページの本文とオプション欄の2箇所にある（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052430/"}}},

    "199": {"name": "北軽井沢 貸別荘 FARMSIDE",
            "reason": "利用規約ページの明示的な否定文「当貸別荘のポリシーによりペット同伴での宿泊はできません。」→pet_ok=no。**coldbath は入れない**: チモシー・ヴィラの設備列挙に「サウナ」と「ジャグジーバス」が別項目で並ぶが、水風呂用途に転用できる旨の明記が無くジャグジーは常時温水の可能性もあるため tub と断定できない。**なおクローバー・ログハウスの設備一覧は「・Wi-Fi・薪ストーブ・サウナ・エアコン…」と薪ストーブとサウナが別の箇条書きで並ぶ**居室ストーブ混同の典型形だが、既存の stove=electric はサウナイキタイ由来でこの公式リストを根拠にしていないため矛盾していない（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://newsite.kitakaruizawafarmstay.com/"}}},

    "225": {"name": "マイグレHOODSTAR",
            "reason": "**capacity=9 の公式根拠が見つかった。** トップに「定員 9名」、本文に「寝室は2部屋をご用意しました。最大9名様までご宿泊いただけます。」と2箇所で明記されており、OTAの9名上限の遺物ではない。「露天風呂・水風呂・オーバーヘッドシャワー・シャワールーム」→coldbath=bath（水風呂が独立項目）、「③絶景×爽やかな心地いい風に包まれる、最高の外気浴スペース」→outdoor_rest=yes。既存値も裏付けが取れた: sauna_type=hut は「デッキに設けたサウナ小屋には」「1F…デッキ、サウナ小屋」の2箇所、loyly=yes は「セルフロウリュでじわじわと」「お好きなだけロウリュを」、wifi=yes は「Wi-Fi 完備」。**stove=electric は裏が取れなかった**: 「フィンランド製の超高熱度サウナストーブHarviaを採用」とあるがHarvia社は電気式・薪式の両方を製造している。薪の取り扱いの案内は見当たらないため電気寄りではあるが断定できない（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 9, "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"},
                         "sauna_type": {"v": "hut", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"},
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.maigre.jp/hoodstar"}}},
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
