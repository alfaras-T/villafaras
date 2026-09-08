#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掲載情報の訂正ツール。設定は FIXES に書く。まず --dry-run で確認すること。"""
import glob, io, json, os, re, sys

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
    "13": {"name": "Ocean's Terrace TORAMII",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「14名」を「12名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "海まで徒歩5分、「大人のアソビゴコロを解放する場所」をコンセプトにしたカリフォルニア風のバケーションハウス。オープンカウンターキッチンや47平米のリビング、33平米のウッドデッキに加え、檜のサウナや露天の星空ジャグジーも備え、最大14名まで宿泊できます。",
            "new_desc": "海まで徒歩5分、「大人のアソビゴコロを解放する場所」をコンセプトにしたカリフォルニア風のバケーションハウス。オープンカウンターキッチンや47平米のリビング、33平米のウッドデッキに加え、檜のサウナや露天の星空ジャグジーも備え、最大12名まで宿泊できます。",
            },
    "53": {"name": "tokoro hotel Isumi",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「7名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "千葉県いすみ市の自然に囲まれた、露天風呂・サウナ・シアタールーム付きの1組限定の宿。築100年以上の古民家を、地域の風土を生かしながらホテルとして改修しています。サウナは滞在中何度でも利用でき、同時に5名まで入れる広さ。最大7名まで宿泊でき、記念日や誕生日にもおすすめです。",
            "new_desc": "千葉県いすみ市の自然に囲まれた、露天風呂・サウナ・シアタールーム付きの1組限定の宿。築100年以上の古民家を、地域の風土を生かしながらホテルとして改修しています。サウナは滞在中何度でも利用でき、同時に5名まで入れる広さ。最大8名まで宿泊でき、記念日や誕生日にもおすすめです。",
            },
    "101": {"name": "KURA YARD",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「13名」を「15名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "2024年3月オープン、築100年以上の古民家をリノベーションした一棟貸切の宿。総面積約198平米、河口湖畔まで徒歩10分という好立地で、最大13名まで宿泊可能です。伝統的な石造りの蔵を改装した2階建てサウナ施設（有料）が自慢で、フィンランド・Harvia社製のストーブと富士山の溶岩を使ったサウナストーンでセルフロウリュを楽しめます。寝室から望む富士山や、美しい日本庭園も見どころです。",
            "new_desc": "2024年3月オープン、築100年以上の古民家をリノベーションした一棟貸切の宿。総面積約198平米、河口湖畔まで徒歩10分という好立地で、最大15名まで宿泊可能です。伝統的な石造りの蔵を改装した2階建てサウナ施設（有料）が自慢で、フィンランド・Harvia社製のストーブと富士山の溶岩を使ったサウナストーンでセルフロウリュを楽しめます。寝室から望む富士山や、美しい日本庭園も見どころです。",
            },
    "138": {"name": "Casablanca Villa Hakone",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「13名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "元箱根の高台、芦ノ湖を望むロケーションに建つ180平米の一棟貸切ヴィラ。通年利用可能な最大38〜40度の温水インフィニティプールとヒノキサウナを完備し、3ベッドルーム・最大13名まで宿泊できます。プールサイドでは別途料金でBBQグリルも利用でき、家族旅行や友人グループ、法人リトリートにも最適です。",
            "new_desc": "元箱根の高台、芦ノ湖を望むロケーションに建つ180平米の一棟貸切ヴィラ。通年利用可能な最大38〜40度の温水インフィニティプールとヒノキサウナを完備し、3ベッドルーム・最大8名まで宿泊できます。プールサイドでは別途料金でBBQグリルも利用でき、家族旅行や友人グループ、法人リトリートにも最適です。",
            },
    "145": {"name": "ICHI-VILLA CROSSROAD HAKONE",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「6名」を「4名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "2025年12月開業、創業396年の老舗旅館「一の湯」が手がける箱根・仙石原の新ブランド一棟貸切ヴィラ。「Cozy×Natural」をテーマに木の温もりと落ち着いた色調で統一され、テントサウナと水風呂、キッチンを完備しています。段差を抑えたユニバーサル設計で車椅子の方も安心して滞在でき、最大6名まで宿泊可能。老舗旅館ならではの安心感とサポート体制のもと、一の湯グループの温泉大浴場も無料で利用できます。",
            "new_desc": "2025年12月開業、創業396年の老舗旅館「一の湯」が手がける箱根・仙石原の新ブランド一棟貸切ヴィラ。「Cozy×Natural」をテーマに木の温もりと落ち着いた色調で統一され、テントサウナと水風呂、キッチンを完備しています。段差を抑えたユニバーサル設計で車椅子の方も安心して滞在でき、最大4名まで宿泊可能。老舗旅館ならではの安心感とサポート体制のもと、一の湯グループの温泉大浴場も無料で利用できます。",
            },
    "151": {"name": "琥珀-AMBER-",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「10名」を「5名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "鎌倉・材木座海岸から徒歩約1分、約100年前の古民家を地元サーファーが和モダンにリノベーションした一棟貸切のバケーションハウス。玄関の土間の先には自炊可能なキッチンとジャグジー付きバスルームがあり、30帖を超えるワンルームに最大10名まで宿泊できます。SUP体験（要予約）や、目の前の海に沈む夕日を眺めながらの滞在が人気です。",
            "new_desc": "鎌倉・材木座海岸から徒歩約1分、約100年前の古民家を地元サーファーが和モダンにリノベーションした一棟貸切のバケーションハウス。玄関の土間の先には自炊可能なキッチンとジャグジー付きバスルームがあり、30帖を超えるワンルームに最大5名まで宿泊できます。SUP体験（要予約）や、目の前の海に沈む夕日を眺めながらの滞在が人気です。",
            },
    "173": {"name": "軽井沢365 フォレストガーデン八風台",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「10名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "軽井沢の中心地から車で約15分、閑静な個人別荘地「八風」の森の奥深くに佇む350坪の一棟貸し宿。「一休Plus+」にも選出された知る人ぞ知る人気施設で、高い天井と天然光・間接照明を巧みに使った空間デザインが特徴です。定員10名、愛犬同伴も可能で、庭には季節によって八風山の雨水が流れる小川も現れます。",
            "new_desc": "軽井沢の中心地から車で約15分、閑静な個人別荘地「八風」の森の奥深くに佇む350坪の一棟貸し宿。「一休Plus+」にも選出された知る人ぞ知る人気施設で、高い天井と天然光・間接照明を巧みに使った空間デザインが特徴です。定員8名、愛犬同伴も可能で、庭には季節によって八風山の雨水が流れる小川も現れます。",
            },
    "201": {"name": "キュレーション熱海桃乃八庵",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「8名」を「6名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "アートや伝統工芸品がちりばめられた、美術館のような最高級の一棟貸切ヴィラ。それぞれデザインテーマが異なる寝室と2つの浴室を備え、温泉とサウナも完備しています。定員8名で、熱海の絶景を望む高台に佇む上質な空間で、非日常のひとときを過ごせます。",
            "new_desc": "アートや伝統工芸品がちりばめられた、美術館のような最高級の一棟貸切ヴィラ。それぞれデザインテーマが異なる寝室と2つの浴室を備え、温泉とサウナも完備しています。定員6名で、熱海の絶景を望む高台に佇む上質な空間で、非日常のひとときを過ごせます。",
            },
    "204": {"name": "オーシャンビュー南熱海",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「12名」を「8名」に、feature の「１２名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "相模湾を一望する高台に佇む絶景ロケーションの貸別荘。緑豊かな自然と紺碧の眺望が広がる別天地で、最上級のリゾート空間が日常から心と体を解き放ってくれます。夏には熱海花火大会も遠望でき、定員12名まで宿泊可能。ゆとりあるバスルームに引き込まれた温泉に浸かりながら、のんびりくつろげます。",
            "new_desc": "相模湾を一望する高台に佇む絶景ロケーションの貸別荘。緑豊かな自然と紺碧の眺望が広がる別天地で、最上級のリゾート空間が日常から心と体を解き放ってくれます。夏には熱海花火大会も遠望でき、定員8名まで宿泊可能。ゆとりあるバスルームに引き込まれた温泉に浸かりながら、のんびりくつろげます。",
            "set_villa": {"feature": "熱海の絶景を見下ろす一棟貸し切り別荘！ テラスでBBQ、最大8名で利用可 花火大会もデッキから遠望できる贅沢な穴場です。温泉は現在停止中"},
            },
    "210": {"name": "熱海オーシャンハウス",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「7名」を「6名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "熱海の高台に建つ温泉付き貸別荘。2LDKの開放感あふれる大きな窓から、熱海の街と海を一望できる絶景が広がります。石風呂の貸切熱海温泉は24時間いつでも楽しめ、最大7名まで宿泊可能。インターネット環境も完備しているためワーケーションにも向いています。",
            "new_desc": "熱海の高台に建つ温泉付き貸別荘。2LDKの開放感あふれる大きな窓から、熱海の街と海を一望できる絶景が広がります。石風呂の貸切熱海温泉は24時間いつでも楽しめ、最大6名まで宿泊可能。インターネット環境も完備しているためワーケーションにも向いています。",
            },
    "215": {"name": "マイグレテラス",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「10名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "2023年2月リニューアル、伊東の高台に建つ一棟貸別荘。小室山や相模湾を望む広々テラスからは天気が良い日には三浦半島や房総半島、初島まで見渡せます。オーナーこだわりのテントサウナはフィンランド製本格ストーブと富士溶岩のサウナストーンを使用し、地下から汲み上げた天然水風呂と伊東温泉の内風呂も完備。シアタールームも備え、最大10名まで団欒できる完全プライベート空間です。",
            "new_desc": "2023年2月リニューアル、伊東の高台に建つ一棟貸別荘。小室山や相模湾を望む広々テラスからは天気が良い日には三浦半島や房総半島、初島まで見渡せます。オーナーこだわりのテントサウナはフィンランド製本格ストーブと富士溶岩のサウナストーンを使用し、地下から汲み上げた天然水風呂と伊東温泉の内風呂も完備。シアタールームも備え、最大8名まで団欒できる完全プライベート空間です。",
            },
    "235": {"name": "COCO VILLA 大室山",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「8名」を「12名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "国指定天然記念物・大室山の圧巻の景観を望む、既存別荘をリノベーションした1日1組限定の宿泊施設。前面ガラス張りのプライベートサウナからは、晴れた日には富士山まで一望でき、四季折々に色を変える大室山の風景を独り占めできます。3LDKの広々とした一軒家に和室・洋室の寝室を備え、最大8名まで宿泊可能。完全無人運営でチェックインからチェックアウトまで非接触、大室山リフトまで徒歩約5分というアクセスの良さも魅力です。",
            "new_desc": "国指定天然記念物・大室山の圧巻の景観を望む、既存別荘をリノベーションした1日1組限定の宿泊施設。前面ガラス張りのプライベートサウナからは、晴れた日には富士山まで一望でき、四季折々に色を変える大室山の風景を独り占めできます。3LDKの広々とした一軒家に和室・洋室の寝室を備え、最大12名まで宿泊可能。完全無人運営でチェックインからチェックアウトまで非接触、大室山リフトまで徒歩約5分というアクセスの良さも魅力です。",
            },
    "264": {"name": "アウトドア貸切別荘北軽井沢2",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（desc の「6名」を「5名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "old_desc": "群馬県嬬恋村の一棟完全貸切別荘。BBQ、焚火、野外サウナがすべて庭に常設されており、食材や薪炭さえ用意すれば滞在中いつでも自由に利用できます。定員6名、洋室2部屋とリビングを備えたシンプルな造りで、事前案内があるため初心者でも安心して本格的なアウトドア体験を楽しめます。",
            "new_desc": "群馬県嬬恋村の一棟完全貸切別荘。BBQ、焚火、野外サウナがすべて庭に常設されており、食材や薪炭さえ用意すれば滞在中いつでも自由に利用できます。定員5名、洋室2部屋とリビングを備えたシンプルな造りで、事前案内があるため初心者でも安心して本格的なアウトドア体験を楽しめます。",
            },
    "58": {"name": "UMIYAMA CHIKURA",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（feature の「6名」を「9名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "set_villa": {"feature": "海・山を望む高台の一棟貸し。バレルサウナ・ウッドデッキテラス。最大9名。ふるさと納税対象。"},
            },
    "190": {"name": "Hygge chalet hakuba（ヒュッゲ シャレー）",
            "reason": "**紹介文の人数が、裏取り済みの定員と食い違っていたので直す（feature の「6名」を「8名」に）。** `tools/prose_cap.py` が挙げた候補。DBの紹介文は初期投入時の文章で、**一次情報で確かめると紹介文のほうが誤っている**のがほとんどという経験則がある（CLAUDE.md）。この施設の `capacity` は出典URL付きで確認済み。**数字だけを差し替え、他の記述には触れていない。**（2026-09）",
            "set_villa": {"feature": "デンマークのHyggeをコンセプトにした一棟貸しシャレー。240平米3LDK、最大8名。サウナ付き。ふるさと納税対象。"},
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
