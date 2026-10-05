# -*- coding: utf-8 -*-
"""从已缓存的公示页 HTML 里提取合同附件链接。"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
cached = Path(os.environ["TEMP"]) / "hhht.html"
raw = cached.read_bytes()
print("bytes:", len(raw))
h = raw.decode("utf-8", errors="replace")
links = re.findall(r'href="([^">]+\.(?:pdf|docx?))"', h, re.I)
if not links:
    # 有些站点用单引号或无引号
    links = re.findall(r"href='?([^'>\s]+\.(?:pdf|docx?))", h, re.I)
for l in links:
    print("LINK:", l)
