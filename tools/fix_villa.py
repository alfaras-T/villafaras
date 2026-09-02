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
    "0": {"name": "古民家宿るうふ 揺之家",
            "reason": "**stove=wood（2026-07・出典なし）を削除する。居室ストーブとの混同の8件目。** 公式を直接取得したところ、**「薪ストーブ」という語がページに一度も登場しない。** 暖房は「空調設備」欄の「ペレットストーブ、エアコン」で、しかもペレットはスキーマの wood/electric/gas のどれでもない。サウナの説明は「杉のサウナと檜の水風呂」「サウナ完備のウッドデッキで夕日を見ながら整う」までで熱源の記載が一切ない。一休の口コミも「薪ストーブも設置されていたので寒い時期は薪ストーブとサウナを楽しめそう」と**両者を並列の別設備**として書いている。sauna_type=indoor は公式の間取りで寝室1・寝室2と並んで「09 - SAUNA」と部屋番号が振られており母屋内の一室として扱われているため。pet_ok=no と wifi は一休 00051840。既存の coldbath=bath / outdoor_rest=yes / kitchen_type=ih / capacity=7 もすべて公式で裏付けが取れた（2026-09確認）",
            "remove_spec": ["stove"],
            "set_spec": {
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"},
                         "capacity": {"v": 7, "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/yuraginoie/"}}},

    "4": {"name": "るうふ別邸 鴨川919",
            "reason": "**同じ「るうふ」ブランドで id=0 と正反対の結果になった。こちらは stove=wood が正しい。** 公式のサウナの説明そのものに「薪ストーブのサウナや水風呂を完備、サウナ後には広いテラスデッキで整う時間を」「薪ストーブのサウナで汗をかき、開放的なテラスでととのう」と**2箇所で明記**されている。**同一ブランドでも棟ごとに違うという原則と、熱源はサウナの説明のなかにあるかで判定するという原則の両方を示す好例。** pet_ok=no と wifi は一休 00051889。既存の coldbath=bath / outdoor_rest=yes / kitchen_type=gas / capacity=8 も公式と一休で裏付け（2026-09確認）",
            "set_spec": {
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://loof-inn.com/hotels/kamogawa919"}}},

    "15": {"name": "amane",
            "reason": "客室ページ「IHクッキングヒーター、オーブンレンジ、シンク」→kitchen_type=ih、室内設備「Wi-Fi」。既存値も裏付けが取れた: 「フラットルームに、本格バレルサウナがプラスされた特別のお部屋。**全1室**」→sauna_exists=room / sauna_type=barrel、「水風呂」「外気浴スペースを確保しています」「定員4名」。**pet_ok=yes は施設単位では正しいが部屋で扱いが違う**: 一休の基本情報は「お泊まりいただけるお部屋はメゾネットルームのみ」で、**サウナ付きのプレミアムフラットルーム自体のページには「※ワンちゃんはご宿泊いただけません」と明記**されている（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "sauna_exists": {"v": "room", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "sauna_type": {"v": "barrel", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-amane.com/rooms/room_02/"}}},

    "16": {"name": "みささ",
            "reason": "**kitchen_type=none をこの項目で3件目として記録する。** 一休の設備欄に「× キッチンあり」と○✕形式で明示。公式の facilities ページにも「キッチン」「調理」「コンロ」の語が一切なく、料理は「専属バトラーが目の前で炭火で焼き上げる」等スタッフ提供が前提で整合する。sauna_type=indoor は「バスエリア：半露天風呂（天然温泉）・サウナ・水風呂（天然水）・シャワーブース」と客室のバスエリアの一部として扱われているため。pet_ok=no は一休の基本情報「不可」＋設備欄「× ペット可」。**既存の loyly / coldbath / outdoor_rest / water_src の出典URL（/room/ と /spa/）は現在404**。サイト再編で /facilities/ に統合されており、出典の張り替えが要る（2026-09確認）",
            "set_spec": {
                         "kitchen_type": {"v": "none", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-misasa.com/facilities/"},
                         "sauna_type": {"v": "indoor", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-misasa.com/facilities/"},
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.awa-misasa.com/facilities/"}}},

    "22": {"name": "海都-kaito- TOKYOBAY",
            "reason": "公式「ペット 不可」＋一休の設備欄「× ペット可」＋基本情報「不可」の三重一致→pet_ok=no。公式「Wi-Fi 有り(無料)」＋一休「wi-fiが利用可能です」の二重一致。公式「テラス（屋外リラックススペース）」→outdoor_rest=yes（インナーテラスは屋内と明確に区別されている）。**stove は入れない**: 「サウナストーブ｜貸別荘のサウナ設備」という見出しはあるが直後に説明文が無く熱源が特定できない（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://piyoresort.com/kaito/room"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://piyoresort.com/kaito/room"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://piyoresort.com/kaito/room"}}},

    "31": {"name": "moe-luana",
            "reason": "一休「wi-fiが利用可能です。有線が利用可能です。」。**capacity=9（2026-07・出典なし）は根拠が無い**: 一休は「1名〜9名」でOTA上限の疑いが濃く、公式サイトにある「最大12名」は**「お客様の声」欄のゲストの感想文**（「最大12名まで宿泊できるようなので、両親や友人家族と…と思いました」）で公式の断定ではない。予約サイト tabichat.jp にも定員の明記が無く、寝具は「ダブルベッド2台、シングルベッド4台、布団2組」。**代替値が確定できないため値は残すが、出典なし capacity=9 のコホートとして要調査**（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051499/"}}},

    "35": {"name": "by the river Isumi",
            "reason": "**stove=wood（2026-07・出典なし）を削除する。居室ストーブとの混同の9件目。** 旅色の紹介記事に「室内にはBoConcept社のソファーや『Morso』の薪ストーブ、ALADDINX社のプロジェクターが備わり」とあり、**ソファ・プロジェクターと並ぶリビングの家具・設備**。サウナ自体の説明は「熱を均一に保つことに優れたバレルサウナ」で熱源の記載が無い。kitchen_type=gas は施設自身の予約サイトの注意事項「外出時や就寝時、ガスコンロ等ご利用、火元に十分ご注意ください」。**coldbath は入れない**: 「木の香りがさわやかな水風呂」は第三者媒体（旅色）のみの情報で公式に記載が無い。**outdoor_rest も入れない**: テラスの存在は確認できるがサウナ後の休憩用途と明記されていない（2026-09確認）",
            "remove_spec": ["stove"],
            "set_spec": {
                         "kitchen_type": {"v": "gas", "src": "desk", "at": "2026-09",
                                        "url": "https://bytheriver.booking.chillnn.com"}}},

    "50": {"name": "THE CLUB 919 DOG FRIENDLY",
            "reason": "既存の capacity=6 に出典を付ける。一休「定員 1名～6名」で、9名上限の機械的読み取りではない。**sauna_type は入れない**: 公式の設備一覧とサウナ専用ページはどちらも「フィンランドサウナの伝統に基づいた本物のロウリュ式サウナ」と様式の呼称のみ。**stove も入れない**: 「サウナストーンから立ち昇る蒸気」までで熱源の明記が無い。**coldbath も入れない**: 設備一覧に「サウナ、ジャグジー」と並記されるのみで水風呂の独立記載が無い（2026-09確認）",
            "set_spec": {
                         "capacity": {"v": 6, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051811/"}}},

    "54": {"name": "Zekkei stay ISUMI cabin",
            "reason": "**stove=wood（2026-07・出典なし）を削除する。居室ストーブとの混同の10件目。** 公式予約サイトの「お子様の宿泊に関して」という**安全上の注意事項**にこうある。「屋外デッキと室内ロフトに手すりがないため、ご自身で安全管理できる場合のみ予約可能です。また薪ストーブもございますので火傷には十分ご注意ください。・川沿いの柵が低いので…」。**手すりのないロフト・川沿いの柵と並ぶ居室の危険箇所の列挙**であり、前後に「サウナ」の語は一切出現しない。**wifi は入れない**: 「※高速インターネットはありますが、携帯電話の電波が不安定になるエリアがございます」は「Wi-Fi」の明記ではない。既存の loyly=yes / coldbath=bath も公式に該当記載が見つからず未確認のまま（2026-09確認）",
            "remove_spec": ["stove"]},

    "56": {"name": "THE VIBES VILLA",
            "reason": "一休の基本情報「ペット 不可」＋設備欄「× ペット可」一致、「wi-fiが利用可能です」。**stove は入れない**: 公式のサウナ専用ページに「ハルビアのサウナヒーターを設置し、セルフロウリュが楽しめる」とあるが、Harvia社は薪式・電気式の両方を製造している。WebSearchの要約には「電気式」とあったが記事本文を直接取得しても該当記載が無く、独立ソースでの裏取りができなかった（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051997/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051997/"}}},

    "58": {"name": "UMIYAMA CHIKURA",
            "reason": "**公式URL（umiyama-chikura.com）が機能していない。** 実機ブラウザで開いたところ、リダイレクトはせず正しいタイトル「UMIYAMA CHIKURA | Official Website」を返すが**本文が一切描画されない空ページ**だった（エージェントは別ブランドへのリダイレクトと報告してきたが再現しなかった）。**既存の sauna_exists / sauna_type / coldbath / capacity / pet_ok / wifi / checkin_method / kids_free の8項目がすべてこのURLを出典としており、再検証できない状態。** 代わりにサウナイキタイの構造化データを使う（住所「千葉県 南房総市 千倉町北朝夷1470番地2」で照合済み）。「セルフロウリュ｜砂時計で時間を計り、30分に1度程度の頻度でお願いします」→loyly=yes、「外気浴 デッキチェア: 2席」→outdoor_rest=yes、「サウナ室：ドライサウナ 対流式（ストーン）電気」→stove=electric。既存の capacity=9 も同ページの施設補足情報「大人6名・子供3名(12歳以下) *お子様含め最大9名様がご宿泊いただけます」で裏付けが取れた。**これは一休の9名上限とは独立した施設側の記載**（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/85685"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/85685"},
                         "stove": {"v": "electric", "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/85685"},
                         "capacity": {"v": 9, "src": "desk", "at": "2026-09",
                                        "url": "https://sauna-ikitai.com/saunas/85685"}}},

    "278": {"name": "LUCY RESORT（ルーシー リゾート）",
            "reason": "公式トップ「グランピング施設の各区画はWIFIを整備」→wifi=yes。**coldbath は入れない**: enjoy ページの「バスジェット付ジャグジー、薪風呂を完備」は文脈上リラクゼーション用の温浴で、サウナ後の冷却用とは書かれていない。**sauna_type / stove も入れない**: 「アウトドアでもサウナが楽しめます！…ストーンに水をかけて自分の好きな温度に調整ができます」までで種類・熱源の明記が無い。**capacity=6 は要検討**: 棟ごとに定員が6/6/5/2/3/3/3名と異なり「全棟利用時は最大N名」という施設全体の数字が見当たらない。既存の6は複数の棟タイプとたまたま一致するだけ（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.lucyresort.com"}}},
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
