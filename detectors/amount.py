from __future__ import annotations

import re

from .base import Span

# 中文大写金额：人民币壹拾贰万叁仟肆佰伍拾陆元整 / 捌拾圆伍角 / 叁拾伍万元整
# 大写字符在合同语境里几乎只用于金额，裸匹配即可（漏报优先）。
CAPITAL = re.compile(
    r"[零壹贰叁肆伍陆柒捌玖拾佰仟万亿]+"
    r"(?:点[零壹贰叁肆伍陆柒捌玖]+)?"
    r"[圆元]"
    r"(?:整|[零壹贰叁肆伍陆柒捌玖]+角(?:[零壹贰叁肆伍陆柒捌玖]+分)?)?"
)


def find_capital_amounts(text: str) -> list[Span]:
    return [
        Span(m.start(), m.end(), m.group(), "AMOUNT", priority=10)
        for m in CAPITAL.finditer(text)
    ]
