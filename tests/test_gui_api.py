# -*- coding: utf-8 -*-
"""无窗测试 gui.app.Api 的 scan/apply 逻辑（不起 pywebview 窗口）。"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from gui.app import Api  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "tests" / "gui_test"
WORK.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    str(ROOT / "tests" / "samples" / "示例采购合同.docx"),
    str(ROOT / "tests" / "samples" / "示例服务合同.pdf"),
    str(ROOT / "tests" / "real" / "contract_harbin.pdf"),
]
api = Api()

print("== scan_batch ==")
r = api.scan_batch(SAMPLES)
for f in r["files"]:
    print(f"  {f['name']}: err={f['err']} hits={len(f['hits'])}")
    assert not f["err"], f"意外错误: {f['err']}"
counts = [len(f["hits"]) for f in r["files"]]
# harbin 第 4 处是页眉公开服务热线 400-810-1996，美式电话规则（3-3-4）会标出，
# 属于"标出来让人决定"的设计行为，不是误报缺陷。
assert counts == [10, 8, 4], counts
print("  命中数 10/8/3 ✓")

f1 = r["files"][0]
print("== 部分勾选：只抹 2 处（金额#￥128,500.00 与 身份证）==")
sels = []
for h in f1["hits"]:
    if h["o"] in ("￥128,500.00", "11010519900307891X"):
        sels.append([h["t"], h["o"], h["occ"]])
assert len(sels) == 2, sels
payload = {"outdir": str(WORK), "files": [{"path": f1["path"], "selections": sels}]}
r2 = api.apply_batch(payload)
res = r2["results"][0]
assert res["ok"] and res["count"] == 2, res
from docx import Document  # noqa: E402
doc = Document(res["out"])
text = "\n".join(p.text for p in doc.paragraphs)
for tb in doc.tables:
    for row in tb.rows:
        for c in row.cells:
            text += "\n" + c.text
assert "￥128,500.00" not in text, "勾选的金额未被抹"
assert "11010519900307891X" not in text, "勾选的身份证未被抹"
assert "13812345678" in text and "壹拾贰万捌仟伍佰元整" in text, "未勾选的内容被误抹"
print("  只抹勾选 2 处，其余保留 ✓")

print("== 空勾选：一处都不抹 ==")
payload0 = {"outdir": str(WORK), "files": [{"path": f1["path"], "selections": []}]}
r3 = api.apply_batch(payload0)
assert r3["results"][0]["ok"] and r3["results"][0]["count"] == 0, r3["results"][0]
print("  count=0 ✓（空勾选不会退化为全抹）")

print("== PDF 部分勾选：harbin 只抹 1 个电话 ==")
f3 = r["files"][2]
sels3 = [[f3["hits"][0]["t"], f3["hits"][0]["o"], 0]]
payload3 = {"outdir": str(WORK), "files": [{"path": f3["path"], "selections": sels3}]}
r4 = api.apply_batch(payload3)
assert r4["results"][0]["ok"] and r4["results"][0]["count"] == 1, r4["results"][0]
import pymupdf  # noqa: E402
pt = "".join(p.get_text() for p in pymupdf.open(r4["results"][0]["out"]))
assert f3["hits"][0]["o"] not in pt, "勾选的电话未抹"
assert f3["hits"][1]["o"] in pt, "未勾选的电话被误抹"
print("  PDF 按勾选精确抹除 ✓")

print("RESULT: PASS")
