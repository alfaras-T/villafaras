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
    "252": {"name": "伊豆高原テントリゾート",
            "reason": "**sauna_type=tent と stove=wood を削除する。出典に挙げた stay.php に根拠が無い。** 同ページを直接取得したところ「サウナ」の語は一度も登場せず、「テント」は宿泊タイプのテント泊（「自然を存分に味わうならやっぱりテント泊。高低差を利用したプライベートな空間となっております。」）を指し、「薪」に至ってはページに存在しない。施設名の「テント」とDBの紹介文にある「BBQや焚き火」から、テントサウナ＋薪ストーブと読み違えたものとみられる。予約サイトの全14プラン（アメニティを「IH用ケトル」レベルまで列挙）にもサウナの記載は無い。validate.py が「sauna_exists が未設定なのにサウナ項目があります」と警告し続けていた不整合の正体。**同じ stay.php から取った kitchen_type=ih は「キッチン（IH）」の記載があり正しい**ので残す。sauna_exists は明示的な否定文が無いため未調査のままとする。あわせて official に付いていた Google 広告のトラッキングパラメータ（?gad_source=1&gclid=…）を除去する（2026-08確認）",
            "set_villa": {"official": "https://tentresort-izu.com/"},
            "remove_spec": ["sauna_type", "stove"]},

    "168": {"name": "湯屋　やまざくら",
            "reason": "一休の設備欄「ペットOK：✕」＋基本情報「ペット：不可」で一致。**sauna_type は入れない**: 温泉・サウナページ「内湯『せせらぎ』2024年6月にリニューアル。プライベートサウナと水風呂付きで」から indoor が有力だが、この「プライベート」は貸切風呂（予約制）の意味で既存の sauna_exists=shared と整合しており、構造の明記ではない。**kitchen_type も入れない**: 客室備品一覧にキッチン関連の記載が無いが、これは「ある物だけを列挙する」形式なので none の根拠にならない（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00031190/"}}},

    "171": {"name": "Noёl HAKONE GENSEN",
            "reason": "公式「Sauna: ロウリュのできるフィンランド式のサウナとジェットバスでじっくりと整う」→loyly=yes、「1Fのバレルサウナは6名様まで利用可能です」→sauna_cap=6（既存の sauna_type=barrel も同文で裏付けられたので出典を付ける）。sauna_exists=yes は公式のSaunaセクションと一休の独立行「サウナ あり」の2ソース。pet_ok=yes は公式「当宿はワンちゃんも一緒にご宿泊いただけます」＋一休「ペット可（5頭まで）」。**stove は入れない**: 「フィンランド式」はスタイルの呼称。**coldbath も入れない**: 「サウナの隣にはジェットバスもご用意しております」とあるがジェットバスは温浴が通例で、水風呂の明記が無い。**wifi も入れない**: 「50台以上の同時接続可能なルーター」はWi-Fiの明記ではない（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://n-o-e-l.com/hakone/gensen"},
                         "sauna_cap": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://n-o-e-l.com/hakone/gensen"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-08",
                                        "url": "https://n-o-e-l.com/hakone/gensen"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://n-o-e-l.com/hakone/gensen"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://n-o-e-l.com/hakone/gensen"}}},

    "176": {"name": "SANU 2nd Home 北軽井沢2nd",
            "reason": "公式マガジン「SANU CABIN MOSS with Sauna」が「サウナ付き客室 提供エリア：北軽井沢2nd／八ヶ岳3rd／白馬1st／河口湖2nd／南アルプス1st」と名指しで列挙しているため一律適用ではない。「サウナ用備品: ロウリュ用バケツ/柄杓、風呂桶…を設置しています」→loyly=yes、「テラスに水風呂とととのい椅子を備えています」→coldbath=bath、「オープンエアの外気浴で心地よいひと時を」→outdoor_rest=yes。pet_ok は一休 00052029 の設備欄「○ペット可」＋基本情報「ペット可」で一致。**stove は入れない**: 一休の口コミに「サウナは電気式で」とあるが口コミは設備の根拠にしない。**sauna_type も入れない**: MOSS型の構造の明記が無い（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"}}},

    "179": {"name": "SANU 2nd Home 白馬1st",
            "reason": "同じMOSS型記事に白馬1stが名指しされている。loyly / coldbath / outdoor_rest は id=176 と同じ根拠。pet_ok は一休 00052076 の設備欄「○ペット可」＋基本情報「ペット可」で一致。**stove は入れない**: 一休の口コミに「入った時の木の香りがお気に入り」「木のいい香りに癒され」とあるが、これは CLAUDE.md が警告する「薪の香り」から wood と誤認するパターンそのもの（2026-08確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.2ndhome-articles.sa-nu.com/sauna-moss"}}},

    "183": {"name": "Hakuba Amber Resort",
            "reason": "住所「北城830-90」の一致を確認し、設備欄「○ペット可」と独立行「サウナ あり」で既存値に出典を付ける。**公式URLが機能していない**: jadehotelgroup.com の EXPLORE HOMES から辿ると sit-jadehotelgroup.gutingjun.com（ステージング環境・読み込み中のまま停止）と jadehotelgroup.gutingjun.com/property/89（「Amber Echoland Mr. T」という別物件。住所が北城3020でDBの830-90と不一致）に着地する。jadegroup.deltahq.com の property-detail は全て404（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051318/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051318/"}}},

    "184": {"name": "Hakuba Jolie Maison",
            "reason": "住所「北城2918-1」の一致を確認。**capacity=9 の既存値（2026-07・出典なし）に裏付けが取れた**: 一休のプラン名に「・人気TYLO高級サウナ・4LDK最大9名」とあり、これは定員欄の機械的な「1～9」ではなく施設固有の記述。pet_ok=yes も設備欄「○ペット可」＋基本情報「ペット可」で一致。**stove は入れない**: プラン名の「TYLO」はスウェーデンの電気サウナヒーターのブランドで electric の有力な手がかりだが、公式側で確認が取れていない。id=283 で HARVIA を根拠にしなかったのと同じ扱いにする（2026-08確認）",
            "set_spec": {
                         "capacity": {"v": 9, "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051589/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00051589/"}}},

    "207": {"name": "パノーラ伊豆赤沢",
            "reason": "出典なしだった4項目すべてに裏付けが取れた。「【調理器具】…IHヒーター・グリル付き3口ガスコンロ」→kitchen_type=both、「定員 6名」、「ペット：本施設は、ペットの同伴は禁止とさせていただいております。」、「ネット環境：Wi-Fi環境あり」。**sauna_exists は入れない**: ページ全文に「サウナ」の文字列が1件も無く、同ページは「ペット: 禁止」「BBQ: 行うことができません」と否定を明示する形式ではあるが、サウナについては否定文が無い。resolstay の不記載を根拠にした否定は2026-08に3件取り消したばかり（2026-08確認）",
            "set_spec": {
                         "kitchen_type": {"v": "both", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/p_izuakazawa/"},
                         "capacity": {"v": 6, "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/p_izuakazawa/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/p_izuakazawa/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/p_izuakazawa/"}}},

    "211": {"name": "オーシャンテラスAtami",
            "reason": "出典なしだった4項目すべてに裏付けが取れた。「定員 8名」、「ペット：本施設は、ペットの同伴は禁止」、「Wi-Fi・デスク・チェアも揃い」、「1名用プライベートサウナと温泉を備えた一棟貸しスイートヴィラ」→sauna_exists=yes（既存の sauna_cap=1 とも整合）。**kitchen_type は入れない**: 調理器具リストの「カセットコンロ」は卓上の携帯コンロで備え付けキッチンの種別ではない（2026-08確認）",
            "set_spec": {
                         "capacity": {"v": 8, "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/oceanterrace/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/oceanterrace/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/oceanterrace/"},
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.resolstay.jp/details/oceanterrace/"}}},

    "232": {"name": "Hiire IZU OLIVE",
            "reason": "同ブランドのFUTO/OMUROからの流用ではなく**OLIVE専用ページで確認**した。注意事項「当施設のサウナは、必ず水着着用の上、ご利用をお願いいたします。特に、水着未着用での屋外の水風呂や整いスペースのご使用は固く禁じられております。」→coldbath=bath / outdoor_rest=yes。sauna_type=indoor は hi-ire.com/stay の「しつらえ」欄が「専用バスルーム／客室サウナ／シャワー／バスタブ」と並べており、同ページが「Hiireは三つの棟に分かれています」として OLIVE/OMURO/FUTO を名指ししているため採用可。wifi も同欄「WiFi／冷蔵庫」。**stove は入れない**: 「エストニア製のサウナをご用意」は原産地であって熱源ではない。pet_ok=yes は既存値だが「当施設では、愛犬とご一緒に過ごす滞在も承っております」で裏付けが取れた（有料オプション・25kg以内中型犬1匹までの条件付き）（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-olive.snack.chillnn.com/ja/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-olive.snack.chillnn.com/ja/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-olive.snack.chillnn.com/ja/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-olive.snack.chillnn.com/ja/"},
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://hiire-izu-olive.snack.chillnn.com/ja/"}}},

    "243": {"name": "Azure Palace 伊豆高原",
            "reason": "公式「大自然の中でサウナと水風呂で整う」→coldbath=bath。pet_ok は一休 00051726 の設備欄「× ペット可」＋基本情報「ペット 不可」で一致。**outdoor_rest は入れない**: 「自然の中の広いお庭をご用意しています。サウナゾーンでは心身から整い、BBQエリアでは…」はサウナが屋外にあることを示唆するが外気浴スペースの明記ではない。**要確認**: 一休のプラン名に「岩盤造りの温泉サウナ」という表記があり既存の sauna_type=tent と印象が異なる（2026-08確認）",
            "set_spec": {
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-08",
                                        "url": "https://azurepalace.net"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://azurepalace.net"}}},

    "244": {"name": "HAKU-AKAZAWA- 【波空】",
            "reason": "公式「FACILITY サウナ：1階のサウナスペースには…水風呂は温度14度前後、バイブラ付き。整いスペースには…」→sauna_type=indoor（建物1階内）。pet_ok は一休 00051755 の設備欄「× ペット可」＋基本情報「ペット 不可」で一致。**なお「水風呂は温度14度前後」は既存の water_temp=t1015（10℃以上15℃未満）と完全に整合し、良い裏付けになった**（2026-08確認）",
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-08",
                                        "url": "https://www.haku-resort.com/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-08",
                                        "url": "https://www.haku-resort.com/"}}},

    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "一休の設備欄「○ペット可」＋基本情報「ペット 可」＋紹介文「ワンちゃんもご一緒に」「ペットフレンドリーの大邸宅」で一致。**capacity=10 の既存値も裏付けが取れた**: 公式「定員：10人」、一休の紹介文も「最大10名まで宿泊できる」。一休の定員欄「1～9名」はOTA上限の遺物（2026-08確認）",
            "set_spec": {
                         "pet_ok": {"v": "yes", "src": "desk", "at": "2026-08",
                                        "url": "https://www.ikyu.com/00052349/"}}},
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
