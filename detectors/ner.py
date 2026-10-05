"""可选的 NER 识别（人名/机构名）。默认不安装、不启用。

启用方式：
    pip install spacy && python -m spacy download en_core_web_sm   # 英文（轻量，~12MB）
    pip install hanlp                                              # 中文（模型较大）

python main.py scan ... --ner        # CLI
GUI 里的 "NER 人名/机构名识别" 开关

多后端按已安装情况自动启用：spaCy 管英文，HanLP 管中文，都没装才报错。
全部本地推理，数据不出机器。首次运行 spaCy/HanLP 各自加载模型（秒级）。
NER 命中的优先级低于正则规则：与金额/证件号等结构化命中重叠时让位。
"""
from __future__ import annotations

from .base import Span

_STATE = None  # 组合后的 finder，进程内缓存


def _tag_to_label(tag: str) -> str | None:
    t = tag.upper()
    if "PERSON" in t or t.endswith("PER"):
        return "PERSON"
    if "ORG" in t:
        return "ORG"
    return None  # LOC/GPE（地址）不在 MVP 范围


# spaCy sm 模型在合同文本里常把缩写/编号误标为机构名或人名，
# 这两类直接丢弃：含数字的实体、以及已知缩写与泛称的停用词表。
_NER_STOP = {
    "ssn", "ein", "iban", "vat", "tel", "fax", "email", "attn", "zip",
    "inc", "llc", "ltd", "co", "corp", "gmbh", "bv",
    "party a", "party b", "the client", "the company", "version",
}


def _spacy_en():
    import spacy

    nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])

    def find(text: str) -> list[Span]:
        out = []
        try:
            doc = nlp(text)
        except Exception:
            return []
        for ent in doc.ents:
            label = _tag_to_label(ent.label_)
            text_ent = ent.text.strip()
            if not label or not text_ent:
                continue
            if any(ch.isdigit() for ch in text_ent):
                continue
            if text_ent.lower().rstrip(".") in _NER_STOP:
                continue
            out.append(Span(ent.start_char, ent.end_char, text_ent,
                            label, source="ner", priority=100))
        return out

    return find


def _hanlp_zh():
    import hanlp

    model = hanlp.load(hanlp.pretrained.ner.msra_ner_albert_base)

    def find(text: str) -> list[Span]:
        try:
            triples = model(text)
        except Exception:
            return []
        out = []
        for item in triples:
            # hanlp 返回形如 ("张三", "PERSON", 0, 2)
            word, tag, start, end = item
            label = _tag_to_label(tag)
            if label and word:
                out.append(Span(start, end, word, label, source="ner", priority=100))
        return out

    return find


def load_ner():
    """返回组合 finder：对一段文本，已安装的各后端结果拼接。"""
    global _STATE
    if _STATE is not None:
        return _STATE

    finders = []
    errors = []
    for name, factory in (("spacy(en)", _spacy_en), ("hanlp(zh)", _hanlp_zh)):
        try:
            finders.append(factory())
        except ImportError:
            errors.append(f"{name} 未安装")
        except Exception as exc:  # 模型损坏等，降级为跳过该后端
            errors.append(f"{name} 加载失败: {exc}")

    if not finders:
        raise SystemExit(
            "未安装任何 NER 后端。英文：pip install spacy && "
            "python -m spacy download en_core_web_sm；中文：pip install hanlp"
        )

    class _Combined:
        def find(self, text: str) -> list[Span]:
            spans: list[Span] = []
            for f in finders:
                spans.extend(f(text))
            return spans

    _STATE = _Combined()
    return _STATE
