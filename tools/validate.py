#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spec-data.js 投入前の検証。

  python3 tools/validate.py                         spec-data.js（マージ後チェック込み）
  python3 tools/validate.py data/desk-research.js   候補ファイル（マージ前チェックのみ）
  python3 tools/validate.py out/spec-data-desk.js data/desk-research.js

選択肢マスタと項目定義は spec.js から読む。エラーがあれば終了コード 1。
"""
import collections, io, json, os, re, subprocess, sys

SPEC = "spec.js"
INDEX = "index.html"
DATA = "spec-data.js"

# 数値項目の妥当範囲。単位の取り違えを機械的に弾くためのもので、
# 「ありえない値」を落とす幅にしてある（疑わしいだけの値は交差チェック側で見る）。
RANGE = {
    "sauna_temp": (40, 130), "sauna_cap": (1, 40), "kitchen_burners": (1, 6),
    "capacity": (1, 120), "comfort_cap": (1, 120), "kids_free": (0, 12),
    "fee_cleaning": (0, 200000), "fee_heating": (0, 200000),
    "fee_pet": (0, 200000), "fee_person": (0, 200000),
    "elevation": (0, 3000), "supermarket": (0, 180), "conveni": (0, 180),
    "onsen": (0, 180), "arrival_real": (0, 600),
}
SAUNA_FIELDS = ["sauna_type", "stove", "sauna_temp", "sauna_cap",
                "loyly", "heat_time", "sauna_hours"]
VALID_SRC = ("owner", "desk", "auto", "review")

# --allow-remove: 訂正で項目を消したときに、削除をエラー扱いしない
ALLOW_REMOVE = False

# 偏り検査の閾値。最頻値がこの割合を超え、かつ出典URL無しがこの割合を超えたら警告する
MIN_BIAS_N = 20      # これ未満の件数では偏りを判定しない
BIAS_SHARE = 0.80
BIAS_NOURL = 0.50


# --------------------------------------------------------------------------
# 走査（文字列・コメントを踏まないための最小スキャナ）
# --------------------------------------------------------------------------
def blank_comments(text):
    """コメントを空白に置換する。改行は残すので文字位置＝行番号が保たれる。"""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "'\"":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def brace_report(text):
    """波括弧の対応を確認する。戻り値は問題のリスト。"""
    s = blank_comments(text)
    depth, problems, opens = 0, [], []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "'\"":
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == "\\" else 1
            if j >= n:
                problems.append((lineno(text, i), "閉じていない文字列"))
            i = j + 1
            continue
        if c == "{":
            depth += 1; opens.append(i)
        elif c == "}":
            depth -= 1
            if depth < 0:
                problems.append((lineno(text, i), "対応しない閉じ括弧 }"))
                depth = 0
            elif opens:
                opens.pop()
        i += 1
    for off in opens:
        problems.append((lineno(text, off), "閉じられていない開き括弧 {"))
    return problems


def lineno(text, off):
    return text.count("\n", 0, off) + 1


def match_brace(s, i):
    """s[i] == '{' の対応する '}' の位置を返す。見つからなければ -1。"""
    depth, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "'\"":
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == "\\" else 1
            i = j + 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def literal(s):
    """ES5 のリテラルを Python の値にする。解析できなければ ('RAW', 原文)。"""
    s = s.strip().rstrip(",").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    if s in ("null", "undefined"):
        return None
    if re.match(r"^-?\d+$", s):
        return int(s)
    if re.match(r"^-?\d*\.\d+$", s):
        return float(s)
    return ("RAW", s)


def parse_pairs(body):
    """`key: value` の並びを (key, 原文, 相対位置) で返す。value は {} でも生値でも可。"""
    out, i, n = [], 0, len(body)
    while i < n:
        while i < n and body[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        m = re.compile(r"([A-Za-z_$][\w$]*|\"\d+\")\s*:\s*").match(body, i)
        if not m:
            out.append((None, body[i:i + 40], i))
            break
        key, j = m.group(1).strip('"'), m.end()
        if j < n and body[j] == "{":
            end = match_brace(body, j)
            if end < 0:
                out.append((key, body[j:], j)); break
            out.append((key, body[j:end + 1], m.start())); i = end + 1
        else:
            k = j
            while k < n:
                c = body[k]
                if c in "'\"":
                    k += 1
                    while k < n and body[k] != c:
                        k += 2 if body[k] == "\\" else 1
                elif c == ",":
                    break
                k += 1
            out.append((key, body[j:k], m.start())); i = k
    return out


# --------------------------------------------------------------------------
# spec.js から選択肢マスタと項目定義を読む
# --------------------------------------------------------------------------
def load_schema():
    s = io.open(SPEC, encoding="utf-8").read()

    m = re.search(r"var O\s*=\s*\{", s)
    if not m:
        sys.exit("!! %s に var O が見つかりません" % SPEC)
    start = m.end() - 1
    block = s[start + 1:match_brace(s, start)]
    masters = {}
    for name, raw, _ in parse_pairs(blank_comments(block)):
        if name and raw.strip().startswith("{"):
            masters[name] = [k for k, _v, _o in parse_pairs(raw.strip()[1:-1]) if k]

    m = re.search(r"var SCHEMA\s*=\s*\[", s)
    if not m:
        sys.exit("!! %s に var SCHEMA が見つかりません" % SPEC)
    tail = s[m.end():]
    rows, order, group = {}, [], None
    for line in tail.split("\n"):
        g = re.search(r"g:\s*'([^']*)'", line)
        if g:
            group = g.group(1)
        r = re.search(r"\{\s*k:\s*'(\w+)'(.*)$", line)
        if not r:
            if re.match(r"\s*\]\s*;", line):
                break
            continue
        key, rest = r.group(1), r.group(2)
        rows[key] = {
            "k": key, "g": group,
            "l": (re.search(r"l:\s*'([^']*)'", rest) or [None, key])[1],
            "o": (re.search(r"o:\s*'(\w+)'", rest) or [None, None])[1],
            "u": (re.search(r"u:\s*'([^']*)'", rest) or [None, None])[1],
            "ch": (re.search(r"ch:\s*'(\w+)'", rest) or [None, None])[1],
        }
        order.append(key)
    for key, row in rows.items():
        if row["o"] and row["o"] not in masters:
            sys.exit("!! %s: 項目 %s の選択肢マスタ '%s' が var O にありません"
                     % (SPEC, key, row["o"]))
    return masters, rows, order


def load_villas():
    s = io.open(INDEX, encoding="utf-8").read()
    m = re.search(r"const VILLAS=(\[.*?\]);", s, re.DOTALL)
    if not m:
        sys.exit("!! %s の VILLAS を読めません" % INDEX)
    return json.loads(m.group(1))


# --------------------------------------------------------------------------
# データファイルの読み込み
# --------------------------------------------------------------------------
def load_data(path, rep, merged):
    text = io.open(path, encoding="utf-8").read()
    for ln, msg in brace_report(text):
        rep.add("ERROR", "波括弧", path, None, None, ln, msg)

    # 「} 改行 識別子:」はカンマ欠落。波括弧の対応は取れてしまうので
    # brace_report では見つからないが、JS としては構文エラーになる。
    for m in re.finditer(r"\}\n\s+(\w+):", text):
        rep.add("ERROR", "構文", path, None, m.group(1), lineno(text, m.start()),
                "項目 %s の直前にカンマがありません" % m.group(1))

    s = blank_comments(text)
    blocks = []
    for m in re.finditer(r'"(\d+)"\s*:\s*\{', s):
        vid, open_at = m.group(1), m.end() - 1
        end = match_brace(s, open_at)
        if end < 0:
            rep.add("ERROR", "波括弧", path, vid, None, lineno(text, open_at),
                    "施設ブロックが閉じていません")
            continue
        fields, order = {}, []
        for key, raw, off in parse_pairs(s[open_at + 1:end]):
            ln = lineno(text, open_at + 1 + off)
            if key is None:
                rep.add("ERROR", "構文", path, vid, None, ln,
                        "解析できない記述: %s" % raw.strip()[:40])
                continue
            if key in fields:
                rep.add("ERROR", "整合性", path, vid, key, ln, "項目が重複しています")
            cell = {"line": ln}
            if raw.strip().startswith("{"):
                for k2, v2, _o2 in parse_pairs(raw.strip()[1:-1]):
                    if k2:
                        cell[k2] = literal(v2)
                if "v" not in cell:
                    rep.add("ERROR", "構文", path, vid, key, ln, "v: がありません")
                    continue
            else:
                cell["v"] = literal(raw)
            fields[key] = cell
            order.append(key)
        blocks.append((vid, fields, lineno(text, open_at)))

    # 同じ id のブロックが複数あるとき、キーが重ならなければ追記（desk-research.js は
    # 調査した順に書き足す一次記録なのでこれが普通）。重なる場合は merge_desk.py が
    # 後のブロックで黙って上書きするため、取りこぼしになる。
    villas, order_seen = {}, []
    for vid, fields, ln in blocks:
        if vid not in villas:
            villas[vid] = {}
            order_seen.append(vid)
        dup = set(villas[vid]) & set(fields)
        if dup:
            rep.add("ERROR", "整合性", path, vid, None, ln,
                    "id が重複し、%s が後のブロックで上書きされます"
                    % ", ".join(sorted(dup)))
        elif villas[vid] and merged:
            rep.add("ERROR", "整合性", path, vid, None, ln,
                    "id が重複しています（マージ後のファイルでは片方が無視されます）")
        villas[vid].update(fields)
    return text, [(v, villas[v], None) for v in order_seen]


# --------------------------------------------------------------------------
# 検証
# --------------------------------------------------------------------------
class Report(object):
    def __init__(self):
        self.items = []

    def add(self, level, stage, path, vid, key, line, msg):
        self.items.append((level, stage, path, vid, key, line, msg))

    def errors(self):
        return [x for x in self.items if x[0] == "ERROR"]

    def dump(self, stage, names, limit=40):
        stages = stage if isinstance(stage, tuple) else (stage,)
        rows = [x for x in self.items if x[1] in stages]
        if not rows:
            print("  問題なし")
            return
        rows.sort(key=lambda x: (x[0] != "ERROR", x[2], int(x[3] or 0), x[5]))
        shown = [x for x in rows if x[0] == "ERROR"][:limit * 4] \
            + [x for x in rows if x[0] != "ERROR"][:limit]
        for level, _st, path, vid, key, line, msg in shown:
            where = "%s:%s" % (os.path.basename(path), line or "-")
            who = "id=%-4s %s" % (vid, names.get(vid, "")[:20]) if vid else ""
            print("  [%s] %-22s %-26s %s%s"
                  % ("×" if level == "ERROR" else "△", where, who,
                     (key + " — ") if key else "", msg))
        if len(rows) > len(shown):
            print("  ... 他 %d 件" % (len(rows) - len(shown)))


def check_fields(path, villas, masters, rows, rep, merged):
    """1〜3段階目: 選択肢照合 / 単位・範囲 / 型。"""
    for vid, fields, _order in villas:
        for key, cell in fields.items():
            ln, v = cell["line"], cell["v"]
            row = rows.get(key)

            if row is None:
                rep.add("ERROR", "型", path, vid, key, ln,
                        "spec.js の SCHEMA にない項目")
                continue
            if isinstance(v, tuple):
                rep.add("ERROR", "型", path, vid, key, ln,
                        "値を解析できません: %s" % v[1][:40])
                continue
            if cell.get("src") is not None and cell.get("src") not in VALID_SRC:
                rep.add("ERROR", "型", path, vid, key, ln,
                        "src '%s' は不正（%s）" % (cell.get("src"), "/".join(VALID_SRC)))
            if cell.get("at") is not None and not re.match(r"^\d{4}-\d{2}$", str(cell["at"])):
                rep.add("WARN", "型", path, vid, key, ln,
                        "at '%s' は YYYY-MM 形式ではありません" % cell["at"])

            if row["o"]:
                valid = masters[row["o"]]
                if isinstance(v, bool):
                    rep.add("ERROR", "型", path, vid, key, ln,
                            "真偽値。選択肢型なのでキーで書く（%s）" % "/".join(valid))
                elif isinstance(v, (int, float)):
                    rep.add("ERROR", "型", path, vid, key, ln,
                            "数値 %s。選択肢型（%s）なのでキーで書く"
                            % (v, "/".join(valid)))
                elif v not in valid:
                    rep.add("ERROR", "選択肢", path, vid, key, ln,
                            "'%s' はマスタ %s にない。有効: %s"
                            % (v, row["o"], "/".join(valid)))
            elif row["u"]:
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    rep.add("ERROR", "型", path, vid, key, ln,
                            "数値項目（単位 %s）に %s が入っています"
                            % (row["u"], "真偽値" if isinstance(v, bool) else "文字列"))
                else:
                    lo, hi = RANGE.get(key, (None, None))
                    if lo is not None and not (lo <= v <= hi):
                        rep.add("ERROR", "単位", path, vid, key, ln,
                                "%s%s は想定範囲 %s〜%s%s の外。単位の取り違えの疑い"
                                % (v, row["u"], lo, hi, row["u"]))
            else:
                if not isinstance(v, str):
                    rep.add("ERROR", "型", path, vid, key, ln,
                            "文字列項目に %r が入っています" % (v,))
                elif key in ("ic", "station") and not re.search(r"\d+\s*分$", v):
                    rep.add("WARN", "単位", path, vid, key, ln,
                            "'%s' が「〜N分」の書式ではありません" % v)

        # 交差チェック（単位の取り違えは範囲だけでは出ないため）
        def val(k):
            c = fields.get(k)
            return c["v"] if c and isinstance(c["v"], (int, float)) \
                and not isinstance(c["v"], bool) else None

        cap, comfort, kids = val("capacity"), val("comfort_cap"), val("kids_free")
        if cap and comfort and comfort > cap:
            rep.add("ERROR", "単位", path, vid, "comfort_cap",
                    fields["comfort_cap"]["line"],
                    "推奨人数 %s名 が定員 %s名 を超えています" % (comfort, cap))
        if cap and kids is not None and kids == cap and cap >= 4:
            rep.add("WARN", "単位", path, vid, "kids_free", fields["kids_free"]["line"],
                    "定員と同値の %s。単位は「歳まで」で人数ではありません" % kids)
        scap = val("sauna_cap")
        if cap and scap and scap > cap * 2:
            rep.add("WARN", "単位", path, vid, "sauna_cap", fields["sauna_cap"]["line"],
                    "サウナ定員 %s名 が施設定員 %s名 の2倍超" % (scap, cap))

        se = fields.get("sauna_exists")
        extra = [k for k in SAUNA_FIELDS if k in fields]
        if se and se["v"] == "no" and extra:
            rep.add("WARN", "整合性", path, vid, "sauna_exists", se["line"],
                    "「なし」なのにサウナ項目があります: %s" % ", ".join(extra))
        # 断片ファイルでは sauna_exists を毎回書かないので、マージ後だけ見る。
        if merged and not se and extra:
            rep.add("WARN", "整合性", path, vid, None, fields[extra[0]]["line"],
                    "sauna_exists が未設定なのにサウナ項目があります: %s"
                    % ", ".join(extra))


def check_merged(path, text, villas, villa_list, rep):
    """マージ後の整合性: 施設数 / id / タグと sauna_exists / 総フィールド数。"""
    ids = set(str(v["id"]) for v in villa_list)
    tags = dict((str(v["id"]), set(v.get("tags") or [])) for v in villa_list)
    names = dict((str(v["id"]), v.get("name", "")) for v in villa_list)

    print("\n=== 施設数 ===")
    print("  %s: %d 施設 / %s: %d 施設"
          % (os.path.basename(path), len(villas), INDEX, len(villa_list)))
    if len(villas) != len(villa_list):
        rep.add("ERROR", "整合性", path, None, None, None,
                "施設数が %d。%s の %d と一致しません"
                % (len(villas), INDEX, len(villa_list)))
        print("  × 施設数が一致しません")
    else:
        print("  ○ 一致")

    for vid, _f, _o in villas:
        if vid not in ids:
            rep.add("ERROR", "整合性", path, vid, None, None,
                    "%s の VILLAS に存在しない id です" % INDEX)
    missing = ids - set(v[0] for v in villas)
    if missing:
        print("  △ spec-data.js に無い施設 %d 件: %s"
              % (len(missing), ", ".join(sorted(missing, key=int)[:10])))

    print("\n=== タグと sauna_exists の整合 ===")
    dist, bad = {}, 0
    for vid, fields, _o in villas:
        cell = fields.get("sauna_exists")
        v = cell["v"] if cell else None
        dist[v] = dist.get(v, 0) + 1
        has = "sauna" in tags.get(vid, set())
        want = v in ("yes", "room")
        if has != want:
            bad += 1
            rep.add("ERROR", "整合性", path, vid, "sauna_exists",
                    cell["line"] if cell else None,
                    "sauna_exists=%s なのにタグは%s"
                    % (v if v else "未調査", "あり" if has else "なし"))
    print("  " + " / ".join("%s %d" % (k if k else "未調査", dist[k])
                            for k in ("yes", "room", "shared", "no", None) if k in dist))
    print("  saunaタグ %d 件 ／ yes+room %d 件"
          % (sum(1 for t in tags.values() if "sauna" in t),
             dist.get("yes", 0) + dist.get("room", 0)))
    print("  %s" % ("○ 一致" if not bad else "× %d 件ずれています" % bad))

    print("\n=== 総フィールド数 ===")
    total = sum(len(f) for _v, f, _o in villas)
    head = git_show(path)
    print("  現在: %d フィールド（%d 施設）" % (total, len(villas)))
    if head is None:
        print("  △ 直前版と比較できませんでした（git 管理外）")
        return
    if head == text:
        print("  ○ HEAD と同一。マージ後ではないため増減は見ません")
        return

    was = head_fields(head)
    now = dict((vid, set(f)) for vid, f, _o in villas)
    base = sum(len(v) for v in was.values())
    gone = [(vid, k) for vid, ks in was.items() for k in ks - now.get(vid, set())]
    print("  HEAD: %d フィールド（差 %+d）" % (base, total - base))

    if gone:
        # 訂正で意図的に消した場合と、マージの取りこぼしを人が見分けられるよう
        # 件数ではなく消えた項目そのものを出す。
        print("  消えた項目 %d 件:" % len(gone))
        for vid, k in sorted(gone, key=lambda x: (int(x[0]), x[1]))[:15]:
            print("      id=%-4s %-16s %s" % (vid, k, names.get(vid, "")[:24]))
        if len(gone) > 15:
            print("      ... 他 %d 件" % (len(gone) - 15))
        if ALLOW_REMOVE:
            print("  ○ --allow-remove 指定のため削除を許容します")
        else:
            rep.add("ERROR", "整合性", path, None, None, None,
                    "HEAD にあった %d フィールドが消えています。"
                    "訂正で消したのなら --allow-remove を付けて再実行" % len(gone))
            print("  × 意図した削除でなければマージの取りこぼしです")
    elif total < base:
        rep.add("ERROR", "整合性", path, None, None, None,
                "総フィールド数が %d 減っています" % (base - total))
        print("  × 減っています")
    elif total == base:
        rep.add("WARN", "整合性", path, None, None, None,
                "内容は変わったのに総フィールド数が HEAD と同じ")
        print("  △ 増えていません")
    else:
        print("  ○ 増えています（削除なし）")

    nourl = sum(1 for _v, f, _o in villas for c in f.values()
                if c.get("src") == "desk" and not c.get("url"))
    desk = sum(1 for _v, f, _o in villas for c in f.values() if c.get("src") == "desk")
    print("\n=== 出典URL ===")
    print("  desk %d 件中 %d 件が url 未記録（%.1f%%）"
          % (desk, nourl, 100.0 * nourl / desk if desk else 0))


def git_show(path):
    try:
        out = subprocess.check_output(["git", "show", "HEAD:%s" % path],
                                      stderr=subprocess.DEVNULL)
    except Exception:
        return None
    return out.decode("utf-8")


def head_fields(text):
    """HEAD 版の vid -> 項目キー集合。"""
    s = blank_comments(text)
    out = {}
    for m in re.finditer(r'"(\d+)"\s*:\s*\{', s):
        end = match_brace(s, m.end() - 1)
        if end > 0:
            ks = set(k for k, _r, _o in parse_pairs(s[m.end():end]) if k)
            out.setdefault(m.group(1), set()).update(ks)
    return out


def check_conflicts(path, villas, rows, names, rep):
    """候補ファイルと spec-data.js で値が食い違う項目を挙げる。

    merge_desk.py は既存優先なので、ここに出るものは spec-data.js に反映されない。
    件数しか出ないと気づけないため、項目そのものを一覧する。
    """
    if not os.path.exists(DATA):
        return
    cur = {}
    s = blank_comments(io.open(DATA, encoding="utf-8").read())
    for m in re.finditer(r'"(\d+)"\s*:\s*\{', s):
        end = match_brace(s, m.end() - 1)
        if end < 0:
            continue
        d = cur.setdefault(m.group(1), {})
        for k, raw, _o in parse_pairs(s[m.end():end]):
            if not k:
                continue
            if raw.strip().startswith("{"):
                for k2, v2, _o2 in parse_pairs(raw.strip()[1:-1]):
                    if k2 == "v":
                        d[k] = literal(v2)
            else:
                d[k] = literal(raw)

    hits = []
    for vid, fields, _o in villas:
        for k, cell in fields.items():
            old = cur.get(vid, {}).get(k)
            if old is not None and str(old) != str(cell["v"]):
                hits.append((vid, k, old, cell["v"], cell["line"]))

    print("\n=== spec-data.js との食い違い ===")
    if not hits:
        print("  なし")
        return
    print("  %d 件。merge_desk.py は既存優先なので、このままでは反映されない。"
          % len(hits))
    by_key = {}
    for h in hits:
        by_key[h[1]] = by_key.get(h[1], 0) + 1
    print("  項目別: " + " / ".join("%s %d" % kv for kv in
                                    sorted(by_key.items(), key=lambda x: -x[1])))
    for vid, k, old, new, ln in sorted(hits, key=lambda x: (x[1], int(x[0])))[:25]:
        print("      %s:%-5s id=%-4s %-14s spec=%-10s 候補=%-10s %s"
              % (os.path.basename(path), ln, vid, k, old, new, names.get(vid, "")[:18]))
    if len(hits) > 25:
        print("      ... 他 %d 件" % (len(hits) - 25))
    rep.add("WARN", "整合性", path, None, None, None,
            "spec-data.js と値が食い違う項目が %d 件。"
            "候補側が正しいなら fix_villa.py で訂正する" % len(hits))


def check_bias(villas, rows, rep, path):
    """一つの値に偏っていて、しかも出典が無い項目を挙げる。

    初期の一括投入で既定値が入ったまま残っている項目を見つけるための検査。
    実例:
      capacity=9      64件（一休の「定員」欄は9名が仕様上限。実定員ではない）
      sauna_exists=yes 273件（着手時。裏を取ると3割が room/shared だった）
    どちらも投入時点でこの検査があれば気づけた。
    """
    label = dict((k, r["l"]) for k, r in rows.items())
    print("\n=== 偏り検査（既定値が残っていないか）===")
    hits = []
    for key in sorted(rows):
        row = rows[key]
        if row.get("ch") == "auto":
            continue          # 座標からの算出値は偏って当然なので見ない
        cnt = collections.Counter()
        withurl = collections.Counter()
        for _v, f, _o in villas:
            c = f.get(key)
            if not c:
                continue
            v = str(c["v"])
            cnt[v] += 1
            if c.get("url"):
                withurl[v] += 1
        tot = sum(cnt.values())
        if tot < MIN_BIAS_N:
            continue
        verified = sum(withurl.values())

        # 規則1: その項目では裏取りが進んでいるのに、この値だけ一件も裏が
        #        取れていない。capacity=9（64件すべて出典なし）がこれ。
        #        割合では引っかからない（64/284=22%）ので件数と均質性で見る。
        #        裏取り前は候補が複数並んで読めなくなるため、最多の1件だけ出し
        #        残りは件数で添える。
        cand = [(n, v) for v, n in cnt.items()
                if n >= MIN_BIAS_N and withurl[v] == 0 and verified > 0]
        if cand:
            cand.sort(reverse=True)
            n, v = cand[0]
            why = "裏取りが一件もない"
            if len(cand) > 1:
                why += "（他に裏取りのない値 %d 種）" % (len(cand) - 1)
            hits.append((n, key, v, n, tot, why))

        # 規則2: 一つの値に極端に偏っていて、大半に出典がない。
        top, n = cnt.most_common(1)[0]
        if (n / float(tot) >= BIAS_SHARE
                and (tot - verified) / float(tot) >= BIAS_NOURL
                and not any(h[1] == key and h[2] == top for h in hits)):
            hits.append((n, key, top, n, tot, "%.0f%% がこの値" % (n / float(tot) * 100)))

    if not hits:
        print("  問題なし")
        return
    for _s, key, v, n, tot, why in sorted(hits, reverse=True):
        print("  [△] %-14s %-8s %3d/%-3d 件 — %s" % (key, v, n, tot, why))
        print("       %s — 既定値のまま残っていないか裏を取ること"
              % label.get(key, key))
        rep.add("WARN", "偏り", path, None, key, None,
                "%s の値 %s に偏り（%d/%d 件、%s）" % (key, v, n, tot, why))


def units_table(villas, rows):
    print("\n=== 単位確認（数値項目の分布）===")
    print("  %-16s %-6s %6s %6s %6s %6s" % ("項目", "単位", "件数", "最小", "中央", "最大"))
    for key in sorted(rows):
        row = rows[key]
        if not row["u"]:
            continue
        vals = sorted(c["v"] for _v, f, _o in villas
                      for k, c in f.items()
                      if k == key and isinstance(c["v"], (int, float))
                      and not isinstance(c["v"], bool))
        if not vals:
            continue
        print("  %-16s %-6s %6d %6s %6s %6s"
              % (key, row["u"], len(vals), vals[0], vals[len(vals) // 2], vals[-1]))


def main():
    global ALLOW_REMOVE
    ALLOW_REMOVE = "--allow-remove" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    paths = args or [DATA]
    for p in paths:
        if not os.path.exists(p):
            sys.exit("!! %s がありません（リポジトリ直下で実行してください）" % p)

    masters, rows, _order = load_schema()
    villa_list = load_villas()
    names = dict((str(v["id"]), v.get("name", "")) for v in villa_list)
    rep = Report()
    print("スキーマ: %s（項目 %d / 選択肢マスタ %d）"
          % (SPEC, len(rows), len(masters)))

    loaded = []
    for p in paths:
        merged = os.path.basename(p) == DATA
        text, villas = load_data(p, rep, merged)
        check_fields(p, villas, masters, rows, rep, merged)
        loaded.append((p, text, villas))
        print("読み込み: %s（%d 施設 / %d フィールド）"
              % (p, len(villas), sum(len(f) for _v, f, _o in villas)))

    print("\n=== 1. 選択肢照合 ===")
    rep.dump("選択肢", names)
    print("\n=== 2. 単位確認 ===")
    rep.dump("単位", names)
    print("\n=== 3. 型チェック ===")
    rep.dump("型", names)
    print("\n=== 構文・波括弧 ===")
    rep.dump(("構文", "波括弧"), names)

    for p, text, villas in loaded:
        if os.path.basename(p) == DATA:
            check_merged(p, text, villas, villa_list, rep)
        else:
            check_conflicts(p, villas, rows, names, rep)
        check_bias(villas, rows, rep, p)
        units_table(villas, rows)

    print("\n=== その他の整合性 ===")
    rep.dump("整合性", names)

    errs = len(rep.errors())
    warns = len(rep.items) - errs
    print("\n" + "-" * 68)
    print("エラー %d 件 / 警告 %d 件" % (errs, warns))
    if errs:
        print("エラーがあります。spec-data.js に入れないでください。")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
