# -*- coding: utf-8 -*-
"""回归测试：同一文件内同一敏感值重复出现时，部分勾选必须精确对应。

历史 bug：扫描端（gui/app.py）按整个文件累计出现序次，apply 端却因
filter_selected 被逐段/逐行调用而重置计数，于是重复值场景下
「取消勾选第 1 处」会把两处都抹掉、「取消勾选第 2 处」则一处都不抹——
两条路都违背「所见即所抹」。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pymupdf as fitz  # noqa: E402
from docx import Document  # noqa: E402

from gui.app import Api  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "tests" / "gui_test"
WORK.mkdir(parents=True, exist_ok=True)
PHONE = "13512345678"

api = Api()


def make_docx(path):
    doc = Document()
    doc.add_paragraph(f"第一段联系电话：{PHONE}。")
    doc.add_paragraph("第二段是无关内容，不含敏感信息。")
    doc.add_paragraph(f"第三段联系电话：{PHONE}。")
    doc.save(path)


def make_pdf(path):
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 100), f"联系电话一：{PHONE}", fontname="china-s", fontsize=11)
    page.insert_text((72, 130), f"联系电话二：{PHONE}", fontname="china-s", fontsize=11)
    pdf.save(path)
    pdf.close()


def hits_for(path):
    res = api.scan_batch([str(path)])
    assert res["files"][0]["err"] is None, res["files"][0]["err"]
    return [h for h in res["files"][0]["hits"] if h["o"] == PHONE]


def apply_one(path, occs):
    sels = [["PHONE", PHONE, o] for o in occs]
    res = api.apply_batch(
        {"outdir": str(WORK), "files": [{"path": str(path), "selections": sels}]}
    )["results"][0]
    assert res["ok"], res
    return Path(res["out"])


print("== docx：同一电话出现在两段 ==")
dx = WORK / "重复值样本.docx"
make_docx(dx)
occ = [h["occ"] for h in hits_for(dx)]
print("  扫描出现序次：", occ)
assert occ == [0, 1], occ

out = apply_one(dx, [1])
lines = [p.text for p in Document(out).paragraphs]
assert PHONE in lines[0], lines
assert PHONE not in lines[2], lines
print("  只抹 occ=1 → 第一段保留、第三段已抹 ✓")

out = apply_one(dx, [0])
lines = [p.text for p in Document(out).paragraphs]
assert PHONE not in lines[0], lines
assert PHONE in lines[2], lines
print("  只抹 occ=0 → 第一段已抹、第三段保留 ✓")

print("== pdf：同一电话出现在两行 ==")
pdf = WORK / "重复值样本.pdf"
make_pdf(pdf)
occ = [h["occ"] for h in hits_for(pdf)]
print("  扫描出现序次：", occ)
assert occ == [0, 1], occ

out = apply_one(pdf, [1])
txt = "\n".join(p.get_text() for p in fitz.open(out))
assert txt.count(PHONE) == 1, txt
assert PHONE in txt  # 第一行保留
print("  只抹 occ=1 → 剩 1 处（第一行保留）✓")

out = apply_one(pdf, [0])
txt = "\n".join(p.get_text() for p in fitz.open(out))
assert txt.count(PHONE) == 1, txt
print("  只抹 occ=0 → 剩 1 处（第二行保留）✓")

print("RESULT: PASS")