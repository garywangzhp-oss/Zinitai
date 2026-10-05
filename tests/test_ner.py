# -*- coding: utf-8 -*-
"""英文 NER 端到端：scan_text(--ner) + app.scan_batch(use_ner=True)。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from detectors import scan_text  # noqa: E402
from gui.app import Api  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

TEXT = ("This Agreement is made between Acme Manufacturing, Inc. and Global Trading LLC. "
        "Authorized representative John Smith shall sign. Contact john.smith@acme-example.com.")
spans = scan_text(TEXT, use_ner=True)
ner = [(s.label, s.text) for s in spans if s.source == "ner"]
print("NER 命中:", ner)
labels = {t for t, _ in ner}
assert "PERSON" in labels and "ORG" in labels, f"人名/机构名缺失: {ner}"
emails = [s.text for s in spans if s.label == "EMAIL"]
assert emails == ["john.smith@acme-example.com"], emails  # 正则与 NER 并存不冲突

print("== GUI scan_batch(use_ner=True) ==")
api = Api()
r = api.scan_batch([str(ROOT / "tests" / "samples" / "en_合成服务合同.docx")], use_ner=True)
hits = r["files"][0]["hits"]
ner_hits = [(h["t"], h["o"]) for h in hits if h["t"] in ("PERSON", "ORG")]
print("GUI NER 命中:", ner_hits)
types = {t for t, _ in ner_hits}
assert "PERSON" in types and "ORG" in types, ner_hits

print("== NER 关闭时无变化 ==")
r2 = api.scan_batch([str(ROOT / "tests" / "samples" / "en_合成服务合同.docx")], use_ner=False)
assert not [h for h in r2["files"][0]["hits"] if h["t"] in ("PERSON", "ORG")]
print("RESULT: PASS")
