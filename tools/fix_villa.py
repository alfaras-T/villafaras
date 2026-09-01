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
    "130": {"name": "那須温泉グランピング Nenn（ネン）",
            "reason": "**sauna_type=barrel（2026-07・出典なし）を削除する。公式の記述と矛盾する。** 公式 /spa/ を直接取得したところ「男性大浴場には、ドライサウナ（最大110℃）、女性大浴場にはミストサウナをご用意しています。」とあり、バレル・テント・小屋のいずれの語も使われていない。**性別で形式が違うため sauna_type に代表値を置けない。**「大浴場に完備しているサウナ」で既存の sauna_exists=shared も裏付けられた。あわせて同ページの「男女どちらにも水風呂（14℃）があり、交互浴でしっかりととのえることができます」から water_temp=t1015 を記録する（同じページの「ドライサウナ（最大110℃）」を sauna_temp=110 として採用済みなので、同じ書式の数値として扱う）（2026-09確認）",
            "remove_spec": ["sauna_type"],
            "set_spec": {
                         "water_temp": {"v": "t1015", "src": "desk", "at": "2026-09",
                                        "url": "https://nenn-nasu.com/spa/"}}},

    "90": {"name": "totonoco 湖畔の隠れ家",
            "reason": "一休の設備欄「× ペット可」＋基本情報「ペット：不可」で両欄一致。既存の capacity=3 も公式「最大収容人数：18名（プライベートヴィラ3名×6室）」と一休「定員：1名～3名」の2ソースで裏付けが取れた（1棟3名）（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052569/"},
                         "capacity": {"v": 3, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00052569/"}}},

    "91": {"name": "ビジョングランピングリゾート山中湖",
            "reason": "公式「無料Wi-Fi」＋一休「wi-fiが利用可能です」。既存値も裏付けが取れた: 一休「部屋内に露天風呂・水風呂・テントサウナがあるため滞在中は完全貸切でご利用いただけます」→sauna_type=tent / coldbath=bath、**「部屋内」なので客室設備であることも確認できた**。**capacity=6 は要検討**: 公式に記載が無く、一休はデラックス「1～6名」スイート「2～8名」で客室数15室。6はデラックスの上限とのみ一致する。**pet_ok=yes も棟限定**: 一休の基本情報に「ペットが泊まれる部屋は『愛犬同伴OK！デラックスグランピング』のみとなります」（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051605/"},
                         "sauna_type": {"v": "tent", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051605/"},
                         "coldbath": {"v": "bath", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051605/"}}},

    "93": {"name": "ヴィラグリファーム七里岩",
            "reason": "**capacity=5（2026-07・出典なし）を11に訂正する。** 公式は「ヴィラ森と風」（大人5名）と「ヴィラ山と空」（大人6名）の2棟構成で、一休に「2棟で大人11名まで宿泊可能」と施設全体の数字が明記されている。既存の5は森と風の単棟のみを読んだもの。id=45 HARUKA KANATA で2棟利用の上限17を採ったのと同じ扱いにする（公式が全棟利用時の数字を出しているならそれを使う）。wifi は一休「wi-fiが利用可能です」（2026-09確認）",
            "set_villa": {"capacity": "11"},
            "set_spec": {
                         "capacity": {"v": 11, "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051403/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.ikyu.com/00051403/"}}},

    "95": {"name": "天空の温泉ヴィラ紬 河口湖",
            "reason": "既存の pet_ok=no に裏付けが取れた。公式「室内での喫煙が確認された場合、別途クリーニング代を請求することがあります。ペット同伴でのご宿泊が確認された場合、別途クリーニング代を請求することがあります。」は**喫煙の禁止と並記された罰則の文脈**であり許可ではない。一休も「× ペット可」「ペット：不可」で3点整合。**kitchen_type=gas は触らない**: 公式は「室内にガスボンベ式のカセットガスコンロを用意」で、カセットコンロを kitchen_type の根拠にしない方針（id=211 / id=24 で同じ判断をした）と食い違うため、既存値の扱いは方針決定待ちとする（2026-09確認）",
            "set_spec": {
                         "pet_ok": {"v": "no", "src": "desk", "at": "2026-09",
                                        "url": "https://global-stays.jp/tsumugi/"}}},

    "106": {"name": "郷音 -G.O.A.T.- The Summit Club",
            "reason": "公式の各棟ページ「セルフ ロウリュウ」→loyly=yes、「露天 ジャグジー」「ゼログラビティチェア x2、サンベッド x2」→outdoor_rest=yes、「IHコンロ、IH対応鍋」→kitchen_type=ih、「Wi-Fi」。既存の stove=wood も公式トップの Sauna 見出し直下で裏付けが取れた: 「聖地『サウナしきじ』の娘の笹野美紀恵がプロデュース。完全オリジナルの薪ストーブ、そして外気浴は目の前に広がる自然の景色で」**サウナ自体の説明のなかに薪ストーブが出てくるので居室ストーブとの混同ではない**。**capacity=16 は要再調査**: /rooms で各棟「定員×4」の表記が繰り返され複数棟の存在も示唆されており、16と整合しない（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://goat-glamping.com/rooms"},
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://goat-glamping.com/rooms"},
                         "kitchen_type": {"v": "ih", "src": "desk", "at": "2026-09",
                                        "url": "https://goat-glamping.com/rooms"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://goat-glamping.com/rooms"},
                         "stove": {"v": "wood", "src": "desk", "at": "2026-09",
                                        "url": "https://goat-glamping.com/rooms"}}},

    "128": {"name": "Haga Farm＆Glamping（芳賀ファーム&グランピング）",
            "reason": "公式「オープンテラスにはソファセットとハモック」→outdoor_rest=yes。既存の capacity=4 も「1棟最大4名様のご利用」「3ベッド・ソファー（4名様の場合3ベッド・ソファーベッド）」で裏付け。**kitchen_type は入れない**: 「アウトドアキッチン（ウェーバー社製ガスグリル、冷蔵庫）」は屋外BBQ用のガスグリルで室内キッチンの加熱方式ではない。**stove も入れない**: 「森のバレルサウナ」は「国産総ヒノキ造り」と素材の記述のみ（2026-09確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://hagafarm.com/cabin/"},
                         "capacity": {"v": 4, "src": "desk", "at": "2026-09",
                                        "url": "https://hagafarm.com/cabin/"}}},

    "138": {"name": "Casablanca Villa Hakone",
            "reason": "公式「テラスには五右衛門風呂を設置。サウナ後の水風呂としてご利用いただけます。お湯を入れれば露天風呂としてもお使いいただけます。」→outdoor_rest=yes（屋外にサウナ後の設備がある）。wifi は一休「wi-fiが利用可能です。」。既存の capacity=8 も一休「定員 1名～8名」「客室数 1室」で裏付けが取れた（8は9名上限の罠ではない）。**なお紹介文は「13名」と書いており食い違う。公式・一休の8を採る**。**coldbath は入れない**: 上の引用は五右衛門風呂を水風呂にも露天風呂にも使えると書いており tub 相当だが、既存値が無く新規に入れるには温冷両用の解釈が要るため次波に回す（2026-09確認）",
            "set_spec": {
                         "outdoor_rest": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://casablancaworld.jp/villa-hakone/"},
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://casablancaworld.jp/villa-hakone/"},
                         "capacity": {"v": 8, "src": "desk", "at": "2026-09",
                                        "url": "https://casablancaworld.jp/villa-hakone/"}}},

    "140": {"name": "ルクス箱根湯本 LUX HAKONE YUMOTO",
            "reason": "公式FAQ「可能です。アロマもご用意しております。」（ロウリュの可否への回答）→loyly=yes。既存の capacity=11 も一休で裏付けが取れた: 「定員 1名～9名」（OTA上限なので不使用）と「3ベッドルームで最大11名までご宿泊」が併記されており、**11は9名罠を正しく回避した値**だった。**outdoor_rest は入れない**: 「温泉露天風呂やプール・デイベッド」の記載はあるがサウナ後の休憩スペースとの明記が無い（2026-09確認）",
            "set_spec": {
                         "loyly": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://lux-hakone.com/faq/"}}},

    "151": {"name": "琥珀-AMBER-",
            "reason": "既存の sauna_exists=yes に出典を付ける。公式「ジャグジーとサウナを完備。」一休「サウナ あり」の2ソース（2026-09確認）",
            "set_spec": {
                         "sauna_exists": {"v": "yes", "src": "desk", "at": "2026-09",
                                        "url": "https://www.treef-vacation-house.com/kohaku-amber"}}},

    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "一休「wi-fiが利用可能です」。住所「〒413-0231 静岡県伊東市富戸1317-2951」の一致も確認した。**outdoor_rest は入れない**: 「ハンモックやインフィニティチェアに揺られながら」はあるがサウナ後の外気浴スペースとの明記が無い（2026-09確認）",
            "set_spec": {
                         "wifi": {"v": "yes", "src": "desk", "at": "2026-09",
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
