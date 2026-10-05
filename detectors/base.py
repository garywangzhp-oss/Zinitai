from __future__ import annotations

from dataclasses import dataclass

# 标签 → 中文显示名（占位符和报告使用）
LABEL_ZH = {
    "AMOUNT": "金额",
    "ID_CARD": "身份证",
    "PHONE": "电话",
    "BANK_ACCOUNT": "银行账号",
    "CREDIT_CODE": "统一社会信用代码",
    "EMAIL": "邮箱",
    "PERSON": "人名",
    "ORG": "机构名",
}


@dataclass
class Span:
    """一段被识别出的敏感文本（在某个文本单元内：docx 一个段落，PDF 一行）"""

    start: int              # 文本单元内的起始偏移
    end: int
    text: str               # 命中的原文
    label: str              # AMOUNT / ID_CARD / ...
    source: str = "regex"   # regex / ner
    priority: int = 0       # 重叠合并时，小者优先保留
    note: str = ""          # 备注（如"未精确定位，按整行抹除"）


def label_zh(label: str) -> str:
    return LABEL_ZH.get(label, label)


def placeholder_for(label: str, seq: int) -> str:
    return f"[{label_zh(label)}#{seq}]"


def merge_spans(spans: list[Span]) -> list[Span]:
    """去掉重叠区间：保留更早出现的；仅当新的完全覆盖旧的时才替换。

    规则表里靠前的（身份证、信用代码等强规则）优先级高，重叠时不会被
    宽匹配的银行卡号规则吞掉。
    """
    if not spans:
        return []
    spans = sorted(spans, key=lambda s: (s.start, -(s.end - s.start), s.priority))
    merged: list[Span] = []
    for s in spans:
        if not merged:
            merged.append(s)
            continue
        last = merged[-1]
        if s.start < last.end:
            # 同起点时只在严格更长时替换，等长时保留先出现的强规则
            # （如身份证必须压过同样 18 位的信用代码宽匹配）
            if s.start <= last.start and s.end > last.end:
                merged[-1] = s
            # 部分重叠：保留先出现的，丢弃后来的
        else:
            merged.append(s)
    return merged
