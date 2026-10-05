from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

import pymupdf as fitz  # PyMuPDF（旧的 `import fitz` 别名已废弃）

from detectors import scan_text
from detectors.base import Span
from .selection import filter_selected
from .selfcheck import residual_warnings


class PdfError(Exception):
    pass


@dataclass
class PdfEdit:
    page_no: int          # 1-based
    rect: fitz.Rect
    span: Span
    context: str
    note: str             # 如"未精确定位，已按整行抹除"


def _open(path):
    try:
        return fitz.open(path)
    except Exception as exc:
        raise PdfError(f"无法打开 PDF：{exc}") from exc


def _page_lines(page):
    """按行产出 (bbox, text, fontsize)。行是 PDF 坐标反查的基本单位。"""
    d = page.get_text("dict")
    for block in d.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(sp.get("text", "") for sp in line.get("spans", []))
            if not text.strip():
                continue
            sizes = [sp.get("size", 10.0) for sp in line.get("spans", []) if sp.get("text", "").strip()]
            fs = max(sizes) if sizes else 10.0
            yield fitz.Rect(line["bbox"]), text, fs


def _assert_text_doc(doc):
    """扫描件检测（在已打开的 doc 上进行）：任何一页几乎没有文本层就报错。"""
    scanned = [i + 1 for i, p in enumerate(doc) if len(p.get_text().strip()) < 20]
    if scanned:
        pages = "、".join(map(str, scanned[:10]))
        raise PdfError(f"第 {pages} 页无文本层，疑似扫描件；MVP 不支持扫描件（需 OCR）")


def assert_text_pdf(path):
    """对外预检接口（GUI 单文件扫描用）：打开 → 检测 → 关闭。"""
    doc = _open(path)
    try:
        _assert_text_doc(doc)
    finally:
        doc.close()


def _doc_text(doc) -> str:
    return "\n".join(p.get_text() for p in doc)


def _locate(page, line_bbox: fitz.Rect, needle: str):
    """把命中文本换算回 PDF 坐标矩形。

    search_for 在全页搜索后按与该行的纵向重叠过滤，避免同文异行的干扰；
    搜不到（字距异常等）时退化为整行抹除并备注。
    """
    try:
        rects = page.search_for(needle)
    except Exception:
        rects = []
    hits = [r for r in rects if r.y0 < line_bbox.y1 - 1 and r.y1 > line_bbox.y0 + 1]
    if hits:
        return hits, ""
    return [line_bbox], "未精确定位，已按整行抹除"


def _context(text: str, span: Span, width: int = 14) -> str:
    a = max(0, span.start - width)
    b = min(len(text), span.end + width)
    return f"…{text[a:span.start]}「{span.text}」{text[span.end:b]}…"


def _iter_page_line_spans(doc, use_ner=False, selected=None, exclude=frozenset()):
    """在已打开的 doc 上逐页逐行产出 (page_no, page, bbox, text, spans)。

    扫描与抹除共用这一条枚举路径：页序 → 行序 → 规则序，
    (label, text, 出现序次) 计数跨全文件累计，顺序确定。
    """
    occ: dict = {}  # 与扫描端一致：整个文件累计，不按行重置
    for pno, page in enumerate(doc, start=1):
        for bbox, text, fs in _page_lines(page):
            spans = [s for s in filter_selected(scan_text(text, use_ner), selected, occ)
                     if s.text not in exclude]
            if spans:
                yield pno, page, bbox, text, fs, spans


def iter_line_spans(path, use_ner=False):
    """GUI 扫描用的轻量枚举：产出 (page_no, line_text, spans)，顺序与 apply 一致。"""
    doc = _open(path)
    try:
        for pno, _page, _bbox, text, _fs, spans in _iter_page_line_spans(doc, use_ner):
            yield pno, text, spans
    finally:
        doc.close()


def scan_pdf(path, use_ner: bool = False):
    """返回 (edits, warnings)。edit 携带页码、矩形、span、上下文。"""
    doc = _open(path)
    edits: list[PdfEdit] = []
    try:
        _assert_text_doc(doc)  # 只打开一次，检测与扫描复用同一个 doc
        for pno, page, bbox, text, _fs, spans in _iter_page_line_spans(doc, use_ner):
            for sp in spans:
                rects, note = _locate(page, bbox, sp.text)
                for r in rects:
                    edits.append(PdfEdit(pno, r, sp, _context(text, sp), note))
    finally:
        doc.close()
    return edits, []


def apply_pdf(path_in, path_out, assign, exclude=frozenset(), use_ner=False, *, selected=None):
    """redaction 真删除 + 占位符回填。返回 (report_items, warnings, 处理处数)。

    selected 语义见 processors/selection.py（keyword-only，GUI 按勾选执行）：
    None 抹全部（减 exclude），否则只抹 (label, text, 出现序次) 命中集合的 span。
    add_redact_annot + apply_redactions 把文字从内容流移除（真删除），
    占位符以 CJK 字体回填在原位置。
    """
    doc = _open(path_in)
    items = []
    n = 0
    warnings: list[str] = []
    try:
        _assert_text_doc(doc)  # 只打开一次，检测与抹除复用同一个 doc
        before_text = _doc_text(doc)
        redacted: Counter = Counter()
        for pno, page, bbox, text, fs, spans in _iter_page_line_spans(
                doc, use_ner, selected, exclude):
            page_edits = []
            for sp in spans:
                redacted[sp.text] += 1  # 逻辑命中计一次（可能对应多个矩形）
                rects, note = _locate(page, bbox, sp.text)
                for r in rects:
                    page_edits.append((r, sp, _context(text, sp), note, min(max(fs, 7), 12)))
            # 计数按逻辑命中（span）而非物理矩形：一次命中可能被
            # search_for 拆成多个相邻矩形，逐矩形计数会虚报。
            for r, sp, ctx, note, f in page_edits:
                ph = assign(sp)
                page.add_redact_annot(
                    r, text=ph, fontname="china-s", fontsize=f,
                    fill=(1, 1, 1), text_color=(0, 0, 0),
                )
                items.append({
                    "placeholder": ph,
                    "label": sp.label,
                    "original": sp.text,
                    "context": ctx,
                    "location": f"第{pno}页",
                    "note": note,
                })
            n += len({id(sp) for _, sp, _ctx, _note, _f in page_edits})
            # apply 必须在每页循环内：注解挂在各自的 page 对象上，
            # 出了循环只剩最后一页的 page 引用，前序页面永远不会被应用。
            if page_edits:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        # 抹后自检：回读文本层，确认本次应抹的原文确实消失。
        # 自检本身失败不能影响抹除结果，故吞掉异常。
        try:
            warnings = residual_warnings(before_text, _doc_text(doc), dict(redacted))
        except Exception:
            warnings = []
        doc.save(path_out, garbage=4, deflate=True)
    finally:
        doc.close()
    return items, warnings, n


def restore_pdf(path_in, path_out, mapping: dict) -> int:
    """按映射表把占位符换回原文（PDF）。返回替换处数。

    两步走，不能合成一步：add_redact_annot(text=原文) 会把替换文字
    压缩进占位符的矩形框里——原文比占位符长时会被缩成几乎不可见的小字。
    所以先真删占位符（不带替换文字），apply 之后再按原字号把原文
    插回占位符左端；超出框宽属预期（PDF 无法像 Word 一样重排）。
    """
    doc = _open(path_in)
    n = 0
    try:
        for page in doc:
            edits = []
            seen: set = set()
            for bbox, text, fs in _page_lines(page):
                for ph, orig in mapping.items():
                    if ph not in text:
                        continue
                    rects, _note = _locate(page, bbox, ph)
                    for r in rects:
                        key = (round(r.x0), round(r.y0), round(r.x1), round(r.y1))
                        if key in seen:
                            continue
                        seen.add(key)
                        edits.append((fitz.Rect(r), orig, min(max(fs, 7), 12)))
            for r, _orig, _f in edits:
                page.add_redact_annot(r, fill=(1, 1, 1))
            if edits:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            for r, orig, f in edits:
                page.insert_text(
                    (r.x0, r.y0 + f * 0.8), orig,
                    fontname="china-s", fontsize=f, color=(0, 0, 0),
                )
                n += 1
        doc.save(path_out, garbage=4, deflate=True)
    finally:
        doc.close()
    return n