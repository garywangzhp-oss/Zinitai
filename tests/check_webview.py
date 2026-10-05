# -*- coding: utf-8 -*-
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import inspect

import webview

print("pywebview settings:", webview.settings)
print("create_window params:", list(inspect.signature(webview.create_window).parameters))
base = os.path.dirname(webview.__file__)
hits = []
for p in glob.glob(os.path.join(base, "**", "*.py"), recursive=True):
    t = open(p, encoding="utf-8", errors="ignore").read()
    if "drag" in t.lower():
        hits.append(os.path.relpath(p, base))
print("files mentioning drag:", hits)
