# -*- coding: utf-8 -*-
"""生成合成英文服务合同（docx + pdf），覆盖全部国际规则 + 误报陷阱。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).resolve().parent / "samples"
OUT.mkdir(parents=True, exist_ok=True)

LINES = [
    ("MASTER SERVICES AGREEMENT", 15),
    ("This Agreement is entered into as of March 15, 2026 by and between:", 11),
    ("Party A: Acme Manufacturing, Inc. (EIN 98-7654321), a Delaware corporation", 11),
    ("Party B: Global Trading LLC, registered office at 1 Harbor Road, Singapore", 11),
    ("Authorized representative of Party A: John Smith (SSN 123-45-6789)", 11),
    ("Contact: john.smith@acme-example.com | Tel: (212) 555-1234 | Cell: +1 415 555 2671", 11),
    ("1. Fees. Client shall pay an initial payment of $1,234.56 upon execution.", 11),
    ("2. Annual license fee: USD 45,000.00, invoiced in advance.", 11),
    ("3. Travel reimbursement shall not exceed EUR 900 or GBP 1,200 per trip.", 11),
    ("4. Total consideration under this Agreement shall not exceed $12,000.", 11),
    ("5. Wire transfers to IBAN GB29 NWBK 6016 1331 9268 19 only.", 11),
    ("6. Card payments to account 4532015112830366 are not accepted.", 11),
    ("7. Order Number 1234567890123 must be quoted on every invoice.", 11),
    ("8. This is Version 2.1 of the form; Section 4.2 survives termination.", 11),
    ("9. Each party owns at least 50% of the voting interest it holds.", 11),
]


def make_docx(out: Path):
    from docx import Document

    doc = Document()
    doc.add_heading("MASTER SERVICES AGREEMENT", level=1)
    for text, _size in LINES[1:]:
        doc.add_paragraph(text)
    doc.save(out)
    print(f"  生成 {out.name}")


def make_pdf(out: Path):
    import pymupdf as fitz

    doc = fitz.open()
    page = doc.new_page()
    body = "\n".join(text for text, _size in LINES)
    rect = fitz.Rect(72, 60, 523, 760)
    page.insert_textbox(rect, body, fontname="china-s", fontsize=10, align=0)
    doc.save(out)
    doc.close()
    print(f"  生成 {out.name}")


if __name__ == "__main__":
    make_docx(OUT / "en_合成服务合同.docx")
    make_pdf(OUT / "en_合成服务合同.pdf")
