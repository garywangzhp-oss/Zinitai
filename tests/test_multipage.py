# -*- coding: utf-8 -*-
"""多页 PDF 抹除回归：两页都有命中时，每一页都必须真删。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pymupdf  # noqa: E402

from gui.app import Api, Assigner  # noqa: E402
from processors import pdf_processor  # noqa: E402

WORK = Path(__file__).resolve().parents[1] / "tests" / "gui_test"
WORK.mkdir(parents=True, exist_ok=True)
src = WORK / "两页合同.pdf"

# 造一份两页 PDF：第 1、2 页各有一个手机号
doc = pymupdf.open()
p1 = doc.new_page()
p1.insert_text((72, 72), "第一页内容：甲方工程部联系电话是13900001111，请在工作时间联系。", fontname="china-s", fontsize=11)
p2 = doc.new_page()
p2.insert_text((72, 72), "第二页内容：乙方商务部联系电话是13800002222，请勿对外透露。", fontname="china-s", fontsize=11)
doc.save(src)
doc.close()

out = WORK / "两页合同_脱敏.pdf"
api = Api()
r = api.scan_batch([str(src)])
hits = r["files"][0]["hits"]
assert len(hits) == 2, f"应扫出 2 处，实际 {len(hits)}"
sels = [[h["t"], h["o"], h["occ"]] for h in hits]
r2 = api.apply_batch({"outdir": str(WORK), "files": [{"path": str(src), "selections": sels}]})
assert r2["results"][0]["ok"] and r2["results"][0]["count"] == 2, r2["results"]

t1 = pymupdf.open(out)[0].get_text()
t2 = pymupdf.open(out)[1].get_text()
assert "13900001111" not in t1, f"第 1 页敏感文字残留！{t1!r}"
assert "13800002222" not in t2, f"第 2 页敏感文字残留！{t2!r}"
assert "[电话#1]" in t1 and "[电话#2]" in t2, (t1, t2)
print("两页均真删 ✓  占位符均回填 ✓")

# 还原验证：占位符换回原文
mp = WORK / "两页合同_脱敏_映射表.json"
import json  # noqa: E402
mapping = {it["placeholder"]: it["original"]
           for it in json.loads(mp.read_text(encoding="utf-8"))["items"]}
restored = WORK / "两页合同_还原.pdf"
n = pdf_processor.restore_pdf(str(out), str(restored), mapping)
rt1 = pymupdf.open(restored)[0].get_text()
rt2 = pymupdf.open(restored)[1].get_text()
assert "13900001111" in rt1 and "13800002222" in rt2, (rt1, rt2)
assert "[电话#1]" not in rt1 and "[电话#2]" not in rt2, (rt1, rt2)
print(f"还原 {n} 处 ✓  原文均已回填、占位符已清除 ✓")
print("RESULT: PASS")
