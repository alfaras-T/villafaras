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
    "6": {"name": "CAP MARTIN Funny house",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/cap-martin-funny-house/hotel/tateyama-jp.html"},
            },
    "20": {"name": "GIFTHOUSE 2nd 館山 洲宮",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/gifthouse-2nd-tateyama-sumiya/hotel/chiba-jp.html"},
            },
    "21": {"name": "UMInoTERRACE",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/uminoterrace-villa-h63734598/hotel/tateyama-jp.html"},
            },
    "23": {"name": "The TRAVELERS Chateau Tateyama",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/travelers-chateau-by-yamato/hotel/chiba-jp.html"},
            },
    "24": {"name": "BEST SPA 99",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/best-spa-99/hotel/chiba-jp.html"},
            },
    "35": {"name": "by the river Isumi",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/by-the-river-isumi-h74734777/hotel/onjuku-jp.html"},
            },
    "41": {"name": "ビーチテラス房総",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h59423077/hotel/kyonan-machi-jp.html"},
            },
    "45": {"name": "HARUKA KANATA 森のヴィラ",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/haruka-kanata-morinovilla/hotel/tateyama-jp.html"},
            },
    "50": {"name": "THE CLUB 919 DOG FRIENDLY",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/the-club-919-dog-friendly/hotel/choshi-jp.html"},
            },
    "57": {"name": "Refwind",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/refwind-h59719600/hotel/kisarazu-jp.html"},
            },
    "60": {"name": "and FOREST勝浦 竹の離れ",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/and-forest-katsuura-takenohanare-h80928005/hotel/onjuku-jp.html"},
            },
    "61": {"name": "天神郷 昊 -Sora-",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h60836376-h60836376/hotel/tateyama-jp.html"},
            },
    "67": {"name": "EKVOLI MARINA VILLA, Isumi Garden",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/ekvoli-marina-villa-isumi-garden/hotel/onjuku-jp.html"},
            },
    "75": {"name": "SANU 2nd Home 八ヶ岳3rd",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sanu-2nd-home-yatsugatake-3rd-h84592342/hotel/hokuto-jp.html"},
            },
    "82": {"name": "古民家宿るうふ　祝之家",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/kominakayado-loof-iwainoie-h47415912/hotel/chuo-shi-jp.html"},
            },
    "85": {"name": "mysa yamanakako",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/mysa-yamanakako/hotel/yamanakako-jp.html"},
            },
    "88": {"name": "hotel norm. fuji",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hotel-norm-fuji/hotel/fujikawaguchiko-jp.html"},
            },
    "92": {"name": "VILLA SAISON FUJI",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/villa-saison-fuji/hotel/fujikawaguchiko-jp.html"},
            },
    "93": {"name": "ヴィラグリファーム七里岩",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h83519055/hotel/nirasaki-jp.html"},
            },
    "106": {"name": "郷音 -G.O.A.T.- The Summit Club",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/the-summit-club-h78671008/hotel/tsuru-jp.html"},
            },
    "111": {"name": "HOTEL SEION FUJI",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hotel-seion-fuji/hotel/yamanakako-jp.html"},
            },
    "117": {"name": "THE SECOND Nasukogen Forest House",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/the-second-nasukogen-forest/hotel/nasu-jp.html"},
            },
    "118": {"name": "SANU 2nd Home 那須1st",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sanu-2nd-home-1st-h68514553/hotel/nasu-jp.html"},
            },
    "120": {"name": "SANU 2nd Home 那須3rd",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sanu-2nd-home-3rd/hotel/nasu-jp.html"},
            },
    "125": {"name": "森deワーケなすっぽ",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/de-h52222874/hotel/nasu-jp.html"},
            },
    "128": {"name": "Haga Farm＆Glamping（芳賀ファーム&グランピング）",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/haga-farm-glamping-h28163821/hotel/utsunomiya-jp.html"},
            },
    "131": {"name": "LEVATA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/levata-nasu-bbq-1-6-h46438761/hotel/nasu-jp.html"},
            },
    "133": {"name": "GEOSPOT MOTOHAKONE B",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/geospot-motohakone-b/hotel/kanagawa-jp.html"},
            },
    "135": {"name": "ASNOVA RESORT FOLQ HAKONE GORA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/asnova-resort-folq-hakone-gora/hotel/hakone-jp.html"},
            },
    "136": {"name": "ASNOVA RESORT NOIE HAKONE SENGOKUHARA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/asnova-resort-noie-hakone-sengokuhara/hotel/nagano-jp.html"},
            },
    "137": {"name": "P's Wood 箱根仙石原",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/p-s-wood/hotel/hakone-jp.html"},
            },
    "140": {"name": "ルクス箱根湯本 LUX HAKONE YUMOTO",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/lux-hakone-yumoto/hotel/hakone-jp.html"},
            },
    "142": {"name": "プライベートリゾート仙居",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h76242687/hotel/nagano-jp.html"},
            },
    "143": {"name": "mysa hakone",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/mysa-hakone/hotel/hakone-jp.html"},
            },
    "144": {"name": "シエロ箱根仙石原",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/villa-cielo-hakone-luxury-mt-fuji-view-private-onsen-sauna/hotel/hakone-jp.html"},
            },
    "153": {"name": "UMITO VILLA KAMAKURA ZAIMOKUZA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/umito-villa-kamakura-zaimokuza/hotel/kamakura-jp.html"},
            },
    "158": {"name": "GIFTHOUSE 三浦 諸磯",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/gifthouse-miura-moroiso/hotel/kanagawa-jp.html"},
            },
    "164": {"name": "HAKONE DOMA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hakone-doma-h82797031/hotel/hakone-jp.html"},
            },
    "172": {"name": "Oyado S",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/oyado-s-h79258576/hotel/hakone-jp.html"},
            },
    "177": {"name": "SANU 2nd Home 蓼科1st",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sanu-2nd-home-tateyama-1st-h83105153/hotel/tateyama-jp.html"},
            },
    "179": {"name": "SANU 2nd Home 白馬1st",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sanu-2nd-home-1st/hotel/hakuba-jp.html"},
            },
    "180": {"name": "GLAMDAY STYLE HOTEL SUITE 山ノ麓",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/glamday-style-hotel-suite-yamanofumoto/hotel/karuizawa-jp.html"},
            },
    "184": {"name": "Hakuba Jolie Maison",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hakuba-jolie-maison/hotel/hakuba-jp.html"},
            },
    "190": {"name": "Hygge chalet hakuba（ヒュッゲ シャレー）",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hygge-chalet-hakuba-h15207772/hotel/hakuba-jp.html"},
            },
    "193": {"name": "SAUNA FOREST CABIN 軽井沢御代田",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sauna-forest-cabin-a-zen-asobi-h33382025/hotel/karuizawa-jp.html"},
            },
    "196": {"name": "Karuizawa Luxe Villa",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/karuizawa-luxe-villa/hotel/karuizawa-jp.html"},
            },
    "225": {"name": "マイグレHOODSTAR",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/maigre-hoodstar-h78339876/hotel/ito-jp.html"},
            },
    "227": {"name": "マイグレA5",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/maigre-a5-h74387464/hotel/ito-jp.html"},
            },
    "228": {"name": "マイグレパノラマ",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/maigre-panorama-h87762596/hotel/ito-jp.html"},
            },
    "230": {"name": "WEAZER西伊豆 廻",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/weazer-kai/hotel/numazu-jp.html"},
            },
    "232": {"name": "Hiire IZU OLIVE",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hiire-izu-olive/hotel/ito-jp.html"},
            },
    "233": {"name": "Hiire IZU OMURO",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/hiire-izu-omuro/hotel/ito-jp.html"},
            },
    "238": {"name": "月と太陽",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sol-and-mani/hotel/okinawa-main-island-jp.html"},
            },
    "239": {"name": "AMAO VILLA",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/amao-villa/hotel/ito-jp.html"},
            },
    "244": {"name": "HAKU-AKAZAWA- 【波空】",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/haku-akazawa/hotel/izu-jp.html"},
            },
    "247": {"name": "SANA 伊豆大室山-Pool Villa-",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/sana/hotel/nagano-jp.html"},
            },
    "249": {"name": "グラン熱川",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h77063707/hotel/izu-jp.html"},
            },
    "250": {"name": "プライベートリゾート南風",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h61696288/hotel/izu-jp.html"},
            },
    "251": {"name": "LAMERVON",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/lamer-von/hotel/atami-jp.html"},
            },
    "253": {"name": "伊豆グランピングリゾートIshiki385",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/izu-glamping-resort-ishiki-385-h50366008/hotel/izu-jp.html"},
            },
    "269": {"name": "THE LOOKOUT KUSATSU",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/the-lookout-kusatsu-vacation-stay-90962v/hotel/kusatsu-jp.html"},
            },
    "274": {"name": "サンライズヴィラ大洗",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/h42088909/hotel/mito-jp.html"},
            },
    "275": {"name": "ときわ邸 M-GARDEN",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/tokiwa-m-garden/hotel/mito-jp.html"},
            },
    "277": {"name": "No.12 Kashima Fan Zone",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/no-12-kashima-fan-zone/hotel/kashima-jp.html"},
            },
    "278": {"name": "LUCY RESORT（ルーシー リゾート）",
            "reason": "**agoda のURLが外国の言語ロケールを指していた。** 日本語サイトの利用者を英語・中国語のページに送っており、**Agoda はロケールが通貨の既定も決める**ため価格表示にも影響する。\n\n全154件のうち `ja-jp` は55件しかなく、外国ロケールが65件（en-in 16 / en-nz 15 / en-sg 12 / en-ie 8 / en-gb 4 / en-za 3 / en-au 3 / en-ca 2 / zh-tw 1 / zh-cn 1）、ロケール無しが34件だった。**Booking は193件すべて `.ja.html` で問題が無かった**ので、収集元によって混ざったとみられる。\n\n**ロケール部分だけを `ja-jp` に差し替え、65件すべてが HTTP 200 を返すことを1件ずつ確認してから当てた。** スラッグと都市名は変えていない。\n\n**ロケール無しの34件は触っていない。** 接続元の言語設定に従って表示されるので、日本の利用者には日本語で出る。（2026-09）",
            "set_villa": {"agoda": "https://www.agoda.com/ja-jp/lucy-resort-vacation-stay-77592v/hotel/tsukuba-jp.html"},
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
