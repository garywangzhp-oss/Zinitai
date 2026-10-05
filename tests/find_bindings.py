# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = io.open("gui/index.html", encoding="utf-8").read().splitlines()
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ("btn-open-folder", "btn-again", "btn-restart",
                             "btn-map", "btn-restore", "renderDone", "dlg-ok",
                             "loadMapping", "mapFiles")):
        print(i, "|", ln.rstrip()[:110])
