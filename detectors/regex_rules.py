from __future__ import annotations

import re

from .base import Span


def _always(_s: str) -> bool:
    return True


def _luhn_ok(digits: str) -> bool:
    """Luhn 校验：过滤掉恰好 13~19 位的订单号、编号等纯数字误报。"""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _credit_ok(s: str) -> bool:
    """信用代码几乎必含字母；纯数字 18 位留给银行卡/身份证规则。"""
    return any(c.isalpha() for c in s)


# (正则, 标签, 后置校验)。顺序即优先级：身份证/信用代码必须在宽匹配的
# 银行账号规则之前，否则 18 位证件号会被当成卡号吞掉。
RULES = [
    (re.compile(r"\d{6}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:[0-2]\d|3[01])\d{3}[\dXx]"),
     "ID_CARD", _always),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "PHONE", _always),
    # 带分隔符的手机号：138-0000-0000 / 138 0000 0000（真实合同常见）
    (re.compile(r"(?<![\d-])1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}(?!\d)"), "PHONE", _always),
    (re.compile(r"(?<!\d)0\d{2,3}-\d{7,8}(?!\d)"), "PHONE", _always),
    (re.compile(r"[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}"),
     "CREDIT_CODE", _credit_ok),
    (re.compile(r"(?<!\d)\d{13,19}(?!\d)"), "BANK_ACCOUNT", _luhn_ok),
    # 金额：货币符号开头（连元字一起吃掉，避免留下孤立的"元"）
    # 小数放宽到 6 位：政采系统常生成 94.500000万元 这类金额
    (re.compile(r"[¥￥]\s*\d[\d,，]*(?:\.\d{1,6})?\s*(?:万)?元?"), "AMOUNT", _always),
    # 数字 + 元（可带 万/亿、千分位、小数、"整"）
    (re.compile(r"(?<!\d)\d[\d,，]*(?:\.\d{1,6})?\s*(?:万|亿)?元(?:人民币)?(?:整)?"),
     "AMOUNT", _always),
    (re.compile(r"人民币\s*[\d,，.]+\s*元?"), "AMOUNT", _always),

    # ==== 英文 / 国际合同 ====
    # 美国社会安全号 SSN：123-45-6789（3-2-4，与 3-3-4 的美式电话区分）
    (re.compile(r"(?<![\d-])\d{3}-\d{2}-\d{4}(?!\d)"), "ID_CARD", _always),
    # 美国雇主识别号 EIN：98-7654321（2-7）
    (re.compile(r"(?<![\d-])\d{2}-\d{7}(?!\d)"), "CREDIT_CODE", _always),
    # 美式电话：(212) 555-1234 / 212-555-1234 / 212.555.1234 / +1 415 555 2671
    # 必须有括号、+1 或分隔符，避免吞掉纯数字订单号
    (re.compile(r"(?<!\d)(?:\+1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])\d{3}[\s.-]?\d{4}(?!\d)"),
     "PHONE", _always),
    # IBAN：连续（GB29NWBK60161331926819）或分组（GB29 NWBK 6016 1331 9268 19）
    (re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{2,4}){3,8}\b"), "BANK_ACCOUNT", _always),
    # 国际货币金额：$1,234.56 / US$5,000.00 / €900 / £1,200 / USD 1,234.56
    (re.compile(r"(?:US\s?|HK\s?|A\s?|C\s?|NZ\s?|S\s?)?[$￥¥€£]\s?\d[\d,，]*(?:\.\d{1,6})?"),
     "AMOUNT", _always),
    (re.compile(r"\b(?:USD|EUR|GBP|CNY|RMB|JPY|HKD|SGD|AUD|CAD|CHF|KRW)\s?\d[\d,，]*(?:\.\d{1,6})?"),
     "AMOUNT", _always),
    # 邮箱（英文合同里最普遍的联系方式）
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "EMAIL", _always),
]


def find_by_rules(text: str) -> list[Span]:
    out: list[Span] = []
    for i, (pattern, label, validator) in enumerate(RULES):
        for m in pattern.finditer(text):
            if validator is None or validator(m.group()):
                out.append(Span(m.start(), m.end(), m.group(), label, priority=i))
    return out
