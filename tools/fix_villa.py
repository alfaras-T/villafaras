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
    "7": {"name": "PREMIUM Funny house",
            "reason": "**stove=wood は正しい。しかも混同を避けたうえでの確認**: ROOM/BATHROOMページの「本格薪サウナと露天風呂」「独立するバスルームとパウダールームから繋がる露天風呂と薪サウナエリア」は**サウナ自体の説明として薪が明記**されている。同じページのLIVING DININGには「リビングコーナーには、薪ストーブ完備」という別の暖房用薪ストーブが独立して存在するが、これとは別物。FAQ「何人まで泊まれますか？ 大人最大5名様」「小型犬一頭のみ宿泊可能です（8,000円/税込）」「全館Wi-Fiをお使いいただけます」、ROOM/KITCHEN欄とFAQの双方に「ガスコンロ」。**ブランド共通のNEWS欄にある「CAP MARTIN Funny house にバレルサウナを新設しました。」は別施設（id=6）の告知なので本施設には適用しない。**なお公式アクセスページの住所表記は「富津市金谷字550番97」でDBの「514-44」と数字が一致しない（地番と住居表示の違いの可能性）（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-premium/faq/"},
                         "capacity": {"v": 5, "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-premium/faq/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-premium/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-premium/faq/"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-08",
                                        "url": "https://beach.funnyfunny.jp/funnyhouse-premium/faq/"}}},

    "11": {"name": "Avalon Cove",
            "reason": "**capacity=9（2026-07・出典なし）を8に訂正する。** 一休は「1名〜9名」でOTA上限のため使えず、公式にも人数の明記が無いが、Airbnb掲載ページの構造化データに occupancy: 8 と入っている。9はOTA上限の遺物とみられる。outdoor_rest は公式「イタリアの高級アウトドア家具Talenti製ソファで夕涼みをしたり」。**stove は既存の electric（一休を出典に記録済み）のまま**。公式の「サウナ（エストニア製HUUMサウナヒーター）」は原文に「電気」の語が無くブランド知識による推定になるため、これ自体は根拠にしない。**kitchen_type は入れない**: 「大型ガス式BBQグリル」は屋外BBQの燃料で室内キッチンの加熱方式ではない。同サイト内のIH言及は別施設 ToramiHouse のもの。**公式URLの評価は見直しが要る**: CLAUDE.md は terracecollections.jp を「リンク集のみ・実体なし」としているが、実際には Avalon Cove 固有の部屋・設備リストを持つ。3施設を1サイトで束ねたブランド公式サイトという性格（2026-08確認）",
            "set_villa": {"capacity": "8"},
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://terracecollections.jp"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://terracecollections.jp"}}},

    "14": {"name": "Sea by TORAMII",
            "reason": "一休の設備欄「ペット可✕」＋基本情報「ペット：不可」で二重に明記。公式は無言及で矛盾なし。**stove は入れない**: 公式 toramii.jp/sea-by-toramii/ を全文確認したが「ストーブ」の語が一度も出てこず、「2024年6月17日に新設されるサウナ」とだけ書かれている。CLAUDE.md にある「2024年7月から…オリジナル小屋＊電気ストーブにグレードアップ」は**同ブランドの別施設 Six on the Beach TORAMII（id=170、神奈川県藤沢市）の記述**であり、この施設のものではない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00050810/"}}},

    "27": {"name": "Sumera Resort Minato",
            "reason": "**coldbath を bath から tub に訂正する。** 公式に「外の浴槽は水風呂としてご利用いただけるほか、温水でのご利用も可能です。」とあり、**専用の水風呂ではなく温冷両用の浴槽**。tub（浴槽・ジャグジー兼用）の定義に合致する。同ページには「プール365日利用可(夏季以外はサウナの水風呂として利用可)」ともあり、季節によってはプールも冷却に使われる。**outdoor_rest は入れない**: 「ガーデンベンチはゆったりと…プールでの休憩やBBQ、そしてファイヤーピットなど、多目的にご利用いただけます。」は BBQ・焚き火まわりの記述で、外気浴という語も出てこない（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "tub", "src": "desk", "at": "2026-08",
                                        "url": "https://sumera.co.jp/minato/"}}},

    "28": {"name": "VACATIONHOUSE TORAMI 7521",
            "reason": "**pet_ok=yes（2026-07・出典なし）は誤り。no が正しい。** 一休 00051438 を直接開いて住所「〒299-4303 千葉県長生郡一宮町東浪見7521-4」がDBと一致することを確認したうえで、設備欄「× ペット可」と基本情報「ペット 不可」の**両方**を確認した。公式 vacationhouse.jp はペットに無言及で矛盾しない。index.html のペットタグも削除する。wifi は一休「Wi-Fi：利用可能」。**capacity=9 は未決着**: 一休は「定員 1名～9名」のみでOTA上限にあたり、公式のトップと information ページを全文確認しても「最大N名」の記載が無い。**loyly は入れない**: 公式「ロウリュウを楽しめるサウナを配置」はセルフ／オートの区別が無い（2026-08確認）",
            "remove_tags": ["pet"],
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051438/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051438/"}}},

    "29": {"name": "PRIVE",
            "reason": "公式トップ「185㎡の広々空間で最大6名が宿泊可能」で既存の capacity=6 に裏付けが取れた（一休の「定員1名〜6名」も9ではないので補強に使える）。pet_ok は一休 00051452 の設備欄「ペット可✕」＋基本情報「ペット：不可」で二重明記、wifi も一休。**公式サイトはサウナに一切言及しない**が、これは既知（CLAUDE.md の「公式に記載が無くてもサウナが実在する5件」の1つ）で否定の根拠にはしない。**outdoor_rest は入れない**: 口コミ欄の「プールサイドでお酒を飲んだり」は施設側の設備説明ではない（2026-08確認）",
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://priveresort.jp/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://priveresort.jp/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://priveresort.jp/"}}},

    "33": {"name": "and RIVER勝浦",
            "reason": "公式「テラスを含め全てのスペースがお客様専用になります」「テラスでは専用のサンダルをご利用下さい」→outdoor_rest=yes。**loyly は入れない**: アメニティ欄の「サウナ用アロマオイル2種」はセルフの傍証だが「セルフ」「オート」の明言が無い。**kitchen_type も入れない**: BBQの「Weber Pulse 1000電気グリル」は屋外専用機材でキッチンとは無関係（2026-08確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://andriver-katsuura.com/"}}},

    "41": {"name": "ビーチテラス房総",
            "reason": "公式トップ「愛犬と泊まれる宿」「超大型犬も泊まれる宿」＋一休の設備欄「ペット可○」・基本情報「ペット：可（1日2棟限定、1頭5,000円）」で既存の pet_ok=yes に裏付けが取れた。wifi は一休。**kitchen_type は入れない**: 「1FテラスではガスタイプのBBQグリルもご利用いただけます」は屋外BBQグリルの燃料で室内キッチンの加熱方式ではない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach-terrace.jp/boso/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://beach-terrace.jp/boso/"}}},

    "46": {"name": "閑閑舎",
            "reason": "設備一覧・FAQ・施設案内の3ページとも情報量が多い。施設案内「テラスに置かれた形状の違うリクライニングチェア」→outdoor_rest=yes、FAQ「大変申し訳ございませんが室内および敷地内の屋外共に、ペットの同伴はお断りさせて頂いております。」→pet_ok=no、FAQ「施設内はWi-Fi対応しております。」。既存値も裏付けが取れた: 施設案内「深さ140cmの水風呂に全身で浸かり」→coldbath=bath、FAQ「大人6名＋子供2名（3歳以下・寝具なし）の最大8名様まで」→capacity=6。**sauna_type / stove は入れない**: サウナは「九十九里の砂を取り入れ、アースバック工法で築いた世界初のサンドウォールサウナ」で、CLAUDE.md のスキーマ不足に挙がっている「サンドウォール」そのもの。熱源も「砂壁がやわらかく熱を蓄え」という蓄熱の描写のみ。**屋外設備の「薪」は FAQ「焚き火の薪はありますか？→中庭のキャビネット内に薪と道具一式」で焚き火用と明示されており、サウナの熱源ではない**（2026-08確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://kankansha.jp/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://kankansha.jp/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://kankansha.jp/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://kankansha.jp/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://kankansha.jp/"}}},

    "57": {"name": "Refwind",
            "reason": "**FAQ が熱源とロウリュを一文で確定させた稀な例。** 「ロウリュウはできますか？→電気式なのでロウリュは出来ません。漏電・故障の原因となるので、おやめください。」→stove=electric / **loyly=no（明示的な否定文）**。FAQ「インターネットは使えますか？→無料のWi-Fiが利用可能です。」、トップ「ハンモックやデッキチェアでのんびり」→outdoor_rest=yes。**sauna_type は入れない**: 「A棟、B棟共にプライベートサウナ」「2時間タイマー」で構造の明言が無い。**なお既存の pet_ok=yes は棟限定**（A棟はペット禁止、B棟のみ可・最大4頭）で、単純な yes/no では表現しきれない（2026-08確認）",
            "set_spec": {
                         "stove": {"v": "electric", "src": "desk", "at": "2026-08",
                                        "url": "https://refwind.jp/faq/"},
                         "loyly": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://refwind.jp/faq/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://refwind.jp/faq/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://refwind.jp/faq/"}}},

    "61": {"name": "天神郷 昊 -Sora-",
            "reason": "**sauna_type を hut から barrel に訂正する。** 既存の出典はふるさと納税ポータル（furusato-tax.jp）という第三者サイトだったが、施設公式に「室内の隅々まで均一に熱と蒸気を行き渡らせる、こだわりのバレルサウナをご用意しております」と明記されている。公式優先の規約に従う。同ページ「同じ空間にはサウナ・水風呂に加え、外気浴に最適なベッドチェアも備えております」→coldbath=bath / outdoor_rest=yes（**スキーマの用語である「外気浴」がそのまま使われている**）。**loyly は入れない**: 「ロウリュによって生まれる蒸気は効率よく循環し」は自然発生的な描写で、一方FAQには「サウナについては…16時〜22時、翌朝6時〜9時までの自動運転となっております（お客様の操作は不要です）」ともあり、この「自動」がロウリュの自動化を指す可能性を排除できない（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://tenjingo-sora.com/facility.html"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://tenjingo-sora.com/facility.html"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://tenjingo-sora.com/facility.html"}}},

    "84": {"name": "mysa fuji",
            "reason": "公式「貸切空間のため、ペットと一緒にご宿泊も可能です。※10kgまでの小型犬２匹まで」＋一休「可（5,000円/1匹、小型犬10kg以内2匹まで）」で既存の pet_ok=yes に裏付けが取れた。wifi は一休「接続可能（wi-fi利用可能）」。既存の loyly=yes は「セルフロウリュを好きなだけ」、outdoor_rest=yes は「森に囲まれた外気スペース」で裏付けられた。capacity=10 も公式「最大宿泊可能人数：10人」で正しく、一休の「1名〜9名」はOTA上限の遺物（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel-mysa-fuji.com/concept/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hotel-mysa-fuji.com/concept/"}}},
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
