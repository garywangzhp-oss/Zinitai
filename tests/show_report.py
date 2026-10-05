# -*- coding: utf-8 -*-
"""打印指定审查报告的命中表。用法: python tests/show_report.py <glob...>"""
import glob
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for pattern in sys.argv[1:]:
    for f in sorted(glob.glob(pattern)):
        print("---", f.replace("\\", "/").split("/")[-1])
        for ln in io.open(f, encoding="utf-8").read().splitlines():
            if ln.startswith("|") and "类型" not in ln and "---" not in ln:
                c = [x.strip() for x in ln.split("|")]
                print("  ", c[2], "|", c[4], "|", c[5][:50])
