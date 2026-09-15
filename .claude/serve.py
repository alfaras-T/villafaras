# -*- coding: utf-8 -*-
"""spec-survey.html の動作確認用のローカルサーバ。開発用のみ。

**リポジトリの場所を決め打ちしない。** 2026-09 にリポジトリを Desktop から
Google ドライブへ移したとき、ここに書いてあった絶対パスだけが取り残された。
このファイルの位置から親をたどる。

`python3 -m http.server` はサンドボックスで `os.getcwd()` が拒否されて
起動しないので、chdir してから使う。
"""
import functools, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("VF_PORT", "8765"))

os.chdir(ROOT)
handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
sys.stderr.write("serving %s on http://127.0.0.1:%d\n" % (ROOT, PORT))
srv.serve_forever()
