"""合同脱敏台 · 桌面应用（pywebview 壳）。

    .venv\\Scripts\\python.exe gui\\app.py

js_api 桥接现有脱敏引擎（detectors/ + processors/），前端 gui/index.html。
所有处理在本机完成，不联网。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import webview

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from detectors.base import label_zh, placeholder_for  # noqa: E402
from processors import docx_processor, pdf_processor  # noqa: E402
from processors.selection import filter_selected  # noqa: E402
from review.report import load_mapping_dict, pair_mapping, write_mapping, write_scan_report  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _base_dir() -> Path:
    """打包 exe：资源在 _MEIPASS 解包目录；开发态：项目根。"""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return ROOT


def _writable_dir() -> Path:
    """可写目录：exe 旁（打包态）或项目根（开发态）。词库放这里。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return ROOT


LEXICON = _writable_dir() / "词库.txt"


def _err(exc: Exception) -> str:
    return f"{exc}"


class Assigner:
    """与 main.py 相同的占位符分配：同批内相同 (类型, 原文) 共享编号。"""

    def __init__(self):
        self._seq: dict = {}
        self._cache: dict = {}

    def __call__(self, span):
        key = (span.label, span.text)
        if key not in self._cache:
            self._seq[span.label] = self._seq.get(span.label, 0) + 1
            self._cache[key] = placeholder_for(span.label, self._seq[span.label])
        return self._cache[key]


class Api:
    """暴露给前端 window.pywebview.api 的方法集合。全部返回可 JSON 序列化对象。"""

    def pick_files(self):
        paths = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("Word或PDF合同 (*.docx;*.pdf)", "所有文件 (*.*)"),
        )
        return {"paths": list(paths or [])}

    def choose_outdir(self, suggest: str | None = None):
        base = suggest or str(Path.home() / "Desktop")
        out = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG, directory=base if os.path.isdir(base) else ""
        )
        return {"dir": out[0] if out else None}

    def scan_batch(self, paths: list[str], use_ner: bool = False):
        files = []
        for i, p in enumerate(paths):
            p = str(p)
            name = os.path.basename(p)
            item = {"id": i, "path": p, "name": name, "err": None,
                    "warnings": [], "hits": []}
            try:
                occ: dict = {}
                if p.lower().endswith(".pdf"):
                    pdf_processor.assert_text_pdf(p)
                    for pno, text, spans in pdf_processor.iter_line_spans(p, use_ner):
                        for sp in spans:
                            k = (sp.label, sp.text)
                            idx = occ.get(k, 0)
                            occ[k] = idx + 1
                            item["hits"].append({
                                "t": sp.label, "o": sp.text,
                                "c": "…" + _context_around(text, sp) + "…",
                                "l": f"第{pno}页", "occ": idx,
                            })
                else:
                    hits, warnings = docx_processor.scan_docx(p, use_ner)
                    item["warnings"] = warnings
                    for h in hits:
                        t = docx_processor.para_text(h.para)
                        for sp in h.spans:
                            k = (sp.label, sp.text)
                            idx = occ.get(k, 0)
                            occ[k] = idx + 1
                            item["hits"].append({
                                "t": sp.label, "o": sp.text,
                                "c": docx_processor.context_of(t, sp),
                                "l": h.desc, "occ": idx,
                            })
            except Exception as exc:  # 单文件失败不拖垮批次
                item["err"] = _err(exc)
            files.append(item)
        return {"ok": True, "files": files}

    def apply_batch(self, payload: dict):
        outdir = payload.get("outdir")
        use_ner = bool(payload.get("use_ner"))
        assigner = Assigner()
        results = []
        for f in payload.get("files", []):
            path = f["path"]
            name = os.path.basename(path)
            stem = Path(path).stem
            f_outdir = Path(f.get("outdir") or outdir or (Path(path).parent / "脱敏结果"))
            f_outdir.mkdir(parents=True, exist_ok=True)
            out = f_outdir / f"{stem}_脱敏{Path(path).suffix.lower()}"
            # 前端永远显式传 selections（可以为空=一处都不抹）；
            # 仅当缺失该键时（CLI 语义）才回退到全抹。
            has_sel = "selections" in f
            sel = {(s[0], s[1], int(s[2])) for s in f.get("selections", [])}
            try:
                if path.lower().endswith(".pdf"):
                    items, warnings, n = pdf_processor.apply_pdf(
                        path, str(out), assigner,
                        selected=set(sel) if has_sel else None, use_ner=use_ner)
                else:
                    items, warnings, n = docx_processor.apply_docx(
                        path, str(out), assigner,
                        selected=set(sel) if has_sel else None, use_ner=use_ner)
                write_mapping(f_outdir / f"{stem}_脱敏_映射表.json", items, warnings)
                write_scan_report(f_outdir / f"{stem}_脱敏_报告.md", name, items, warnings)
                results.append({"name": name, "out": str(out), "count": n,
                                "warnings": warnings, "ok": True})
            except Exception as exc:
                results.append({"name": name, "ok": False, "error": _err(exc)})
        return {"ok": True, "results": results, "outdir": str(outdir or "")}

    def restore_batch(self, paths):
        results = []
        outdir = ""
        for p in paths:
            p = str(p)
            stem = Path(p).stem
            mp = pair_mapping(p)
            if not mp:
                results.append({"name": os.path.basename(p), "ok": False,
                                "error": f"同目录未找到映射表（{stem}_映射表.json）"})
                continue
            try:
                mapping = load_mapping_dict(mp)
                out_stem = stem.replace("_脱敏", "_还原")
                out = Path(p).parent / f"{out_stem}{Path(p).suffix.lower()}"
                if p.lower().endswith(".pdf"):
                    n = pdf_processor.restore_pdf(p, str(out), mapping)
                else:
                    n = docx_processor.restore_docx(p, str(out), mapping)
                outdir = str(Path(p).parent)
                results.append({"name": os.path.basename(p), "out": str(out),
                                "count": n, "warnings": [], "ok": True})
            except Exception as exc:
                results.append({"name": os.path.basename(p), "ok": False, "error": _err(exc)})
        return {"ok": True, "results": results, "outdir": outdir}

    def read_mapping(self, path: str):
        try:
            return {"ok": True, "text": Path(path).read_text(encoding="utf-8")}
        except Exception as exc:
            return {"ok": False, "error": _err(exc)}

    def open_path(self, path: str):
        try:
            if os.path.isdir(path):
                os.startfile(path)  # noqa: S606
            else:
                os.startfile(os.path.dirname(path) or ".")  # noqa: S606
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": _err(exc)}

    def open_lexicon(self):
        try:
            if not LEXICON.exists():
                LEXICON.write_text(
                    "# 排除词库：一行一条原文（精确匹配），命中的不抹除。\n"
                    "# 例如对外公开的电话、编号等。\n", encoding="utf-8")
            os.startfile(str(LEXICON))  # noqa: S606
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": _err(exc)}


def _context_around(text: str, span, width: int = 14) -> str:
    a = max(0, span.start - width)
    b = min(len(text), span.end + width)
    return f"{text[a:span.start]}「{span.text}」{text[span.end:b]}"


def main():
    index = _base_dir() / "gui" / "index.html"
    webview.create_window(
        "紫泥台",
        str(index),
        js_api=Api(),
        width=1280, height=820,
        min_size=(960, 700),
        background_color="#FAFAF7",
    )
    webview.start()


if __name__ == "__main__":
    main()
