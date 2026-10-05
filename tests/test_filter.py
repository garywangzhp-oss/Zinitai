# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
r = re.compile(r"^([\w ]+)\((\*(?:\.(?:\w+|\*))*(?:;\*(?:\.(?:\w+|\*))*)*)\)$")
for cand in [
    "Word / PDF 合同 (*.docx;*.pdf)",
    "Word或PDF合同 (*.docx;*.pdf)",
    "合同文档 (*.docx;*.pdf)",
]:
    print(bool(r.match(cand)), cand)
