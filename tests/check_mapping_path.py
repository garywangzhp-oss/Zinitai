# -*- coding: utf-8 -*-
"""验证 GUI 映射表路径推导与后端写入文件名一致。"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

out = "D:/out/Purchase+Contract-NWC-704106-0824-Final_脱敏.pdf"
mp = re.sub(r"_脱敏\.\w+$", "_脱敏_映射表.json", out)
print("推导路径:", mp)
assert mp.endswith("Purchase+Contract-NWC-704106-0824-Final_脱敏_映射表.json"), mp

# 与后端实际写入名对齐：后端用的是“原始输入路径”的 stem
# （app.py: stem = Path(path).stem；path 是用户选的原始合同）
input_path = "D:/out/Purchase+Contract-NWC-704106-0824-Final.pdf"
backend = Path(input_path).parent / f"{Path(input_path).stem}_脱敏_映射表.json"
assert mp == str(backend).replace("\\", "/"), (mp, backend)
print("与后端写入名一致 ✓")
