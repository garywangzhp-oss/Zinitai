from __future__ import annotations

from .amount import find_capital_amounts
from .base import Span, label_zh, merge_spans, placeholder_for
from .regex_rules import find_by_rules


def scan_text(text: str, use_ner: bool = False) -> list[Span]:
    """对一个文本单元（docx 一个段落 / PDF 一行）做识别，返回合并后的 Span。"""
    spans = find_by_rules(text)
    spans.extend(find_capital_amounts(text))
    if use_ner:
        from .ner import load_ner

        spans.extend(load_ner().find(text))
    return merge_spans(spans)
