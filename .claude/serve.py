# -*- coding: utf-8 -*-
"""spec-survey.html の動作確認用のローカルサーバ。開発用のみ。"""
import os, sys
ROOT = "/Users/T/Desktop/villafaras"
os.chdir(ROOT)
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
H = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
srv = ThreadingHTTPServer(("127.0.0.1", 8765), H)
sys.stderr.write("serving %s on http://127.0.0.1:8765\n" % ROOT)
srv.serve_forever()
