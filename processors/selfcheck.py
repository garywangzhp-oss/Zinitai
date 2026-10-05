"""抹后自检：确认「本次应抹掉」的原文确实消失（漏报优先原则的兜底）。

只产出警告文字，不改变抹除行为；自检自身出错必须不影响抹除结果
（调用方用 try/except 兜住）。
"""
from __future__ import annotations


def residual_warnings(before_text: str, after_text: str, redacted: dict) -> list[str]:
    """redacted: {原文: 本次实际抹除的逻辑命中数}。

    原文只有在「本次抹掉的次数覆盖了它原本出现的次数」时才应完全消失；
    届时仍能提取到，说明有命中没被真正抹除。按出现次数比较，这样
    "同一值出现多次、只勾了其中一处" 不会被误报。

    尽力而为的启发式：文本层提取的断行/空格可能与识别时不同，
    匹配不到不报错，只报「本该没了却还在」。
    """
    residual = []
    for text, n in redacted.items():
        if not text:
            continue
        if after_text.count(text) > max(0, before_text.count(text) - n):
            residual.append(text)
    if not residual:
        return []
    shown = "、".join(f"`{r}`" for r in residual[:8])
    more = f"（共 {len(residual)} 处）" if len(residual) > 8 else ""
    return [
        f"抹除后自检：以下原文仍可被提取，可能有命中未真正抹除，请人工复查：{shown}{more}"
    ]