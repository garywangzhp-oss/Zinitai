# -*- coding: utf-8 -*-
"""英文/国际规则单元验证：命中集 + 误报陷阱。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from detectors import scan_text  # noqa: E402

TEXT = (
    "Party A: Acme Manufacturing, Inc. (EIN 98-7654321). "
    "Representative John Smith (SSN 123-45-6789). "
    "Contact john.smith@acme-example.com | Tel (212) 555-1234 | Cell +1 415 555 2671. "
    "Initial payment $1,234.56; annual fee USD 45,000.00; cap EUR 900 or GBP 1,200; "
    "total not exceed $12,000. Wire to IBAN GB29 NWBK 6016 1331 9268 19 "
    "or account 4532015112830366. Quote Order 1234567890123. Version 2.1, "
    "Section 4.2, at least 50% voting interest, effective March 15, 2026."
)

spans = scan_text(TEXT)
found = {(s.label, s.text) for s in spans}
print("命中：")
for s in sorted(spans, key=lambda x: x.start):
    print(f"  {s.label:12s} {s.text}")

EXPECT = {
    ("CREDIT_CODE", "98-7654321"),
    ("ID_CARD", "123-45-6789"),
    ("EMAIL", "john.smith@acme-example.com"),
    ("PHONE", "(212) 555-1234"),
    ("PHONE", "+1 415 555 2671"),
    ("AMOUNT", "$1,234.56"),
    ("AMOUNT", "USD 45,000.00"),
    ("AMOUNT", "EUR 900"),
    ("AMOUNT", "GBP 1,200"),
    ("AMOUNT", "$12,000"),
    ("BANK_ACCOUNT", "GB29 NWBK 6016 1331 9268 19"),
    ("BANK_ACCOUNT", "4532015112830366"),
}
missing = EXPECT - found
for m in sorted(missing):
    print("!! 漏：", m)

FORBID = ["1234567890123", "2.1", "4.2", "50%", "March 15, 2026", "9001"]
banned = [t for (_, t) in found for f in FORBID if t == f]
extra_bad = [t for (_, t) in found if t in FORBID]
for b in extra_bad:
    print("!! 误报：", b)

ok = not missing and not extra_bad
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
