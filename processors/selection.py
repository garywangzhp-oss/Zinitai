"""按出现序次筛选命中：GUI 的"所见即所抹"依赖它。

selected 为 None 时全收（CLI 行为）；否则只保留 (label, text, 第几次出现)
三元组命中的 span。出现序次在整个文件内累计（与扫描端 gui/app.py、与占位符分配口径一致）：
counter 必须由调用方跨段落/跨页行持有并透传。若每次调用都新建计数，同一文件里
重复出现的值会互相错位——要么漏抹，要么把没勾的也抹掉。
"""


def filter_selected(spans, selected, counter=None):
    if selected is None:
        return spans
    counts: dict = {} if counter is None else counter
    out = []
    for s in spans:
        key = (s.label, s.text)
        idx = counts.get(key, 0)
        counts[key] = idx + 1
        if (s.label, s.text, idx) in selected:
            out.append(s)
    return out
