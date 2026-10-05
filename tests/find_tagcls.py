# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for i, ln in enumerate(io.open("gui/index.html", encoding="utf-8"), 1):
    if "TYPES =" in ln or "fmtType" in ln:
        print(i, "|", ln.rstrip())
