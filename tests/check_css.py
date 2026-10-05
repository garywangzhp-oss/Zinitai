# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
needles = [".hits{", ".hitsbar{", ".hitlist{", ".empty-wrap{", ".done-wrap{",
           "body{", ".masthead{", ".workspace{", ".actionbar{", ".filelist{"]
for ln in io.open("gui/index.html", encoding="utf-8"):
    s = ln.strip()
    for n in needles:
        if s.startswith(n):
            print(s[:110])
