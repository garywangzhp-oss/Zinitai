# -*- coding: utf-8 -*-
import glob
import os
import sys

import webview

out = []
base = os.path.dirname(webview.__file__)
for p in glob.glob(os.path.join(base, "**", "*.py"), recursive=True):
    t = open(p, encoding="utf-8", errors="ignore").read()
    if "file filter" in t or "file_types" in t and "re." in t:
        for i, line in enumerate(t.splitlines(), 1):
            if "filter" in line.lower() and ("re." in line or "valid" in line.lower()):
                out.append(f"{p} #{i}: {line.strip()}")
open(os.path.join(os.path.dirname(__file__), "filter_findings.txt"), "w", encoding="utf-8").write("\n".join(out))
print("wrote", len(out), "findings")
