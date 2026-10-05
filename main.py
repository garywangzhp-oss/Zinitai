"""合同脱敏工具 CLI。

    python main.py scan  <文件或目录> [-o 输出目录] [--ner]
    python main.py apply <文件或目录> [-o 输出目录] [--exclude 词库.txt] [--ner]

scan 只识别并输出审查报告，不改文件；apply 重新识别并执行抹除，
两步对同一文件的识别结果一致（同一套规则）。
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from detectors.base import label_zh, placeholder_for
from processors import docx_processor, pdf_processor
from processors.docx_processor import DocxError
from processors.pdf_processor import PdfError
from review.report import write_mapping, write_scan_report

try:  # 个别字符在旧控制台代码页下缺字形时，用占位符代替而不是报错
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

REDACTED_SUFFIX = "_脱敏"


class Assigner:
    """占位符分配：相同 (类型, 原文) 在整个批次里拿到相同编号。"""

    def __init__(self):
        self._seq: Counter = Counter()
        self._cache: dict[tuple[str, str], str] = {}

    def __call__(self, span) -> str:
        key = (span.label, span.text)
        if key not in self._cache:
            self._seq[span.label] += 1
            self._cache[key] = placeholder_for(span.label, self._seq[span.label])
        return self._cache[key]

    def total(self) -> int:
        return sum(self._seq.values())


def load_exclude(path: str | None) -> frozenset[str]:
    if not path:
        return frozenset()
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    words = {ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")}
    print(f"  已加载词库：{len(words)} 条（原文精确匹配不抹）")
    return frozenset(words)


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files = []
    for p in sorted(target.iterdir()):
        if p.suffix.lower() in (".docx", ".pdf") \
                and not p.name.startswith("~$") \
                and not p.stem.endswith(REDACTED_SUFFIX):
            files.append(p)
    return files


def out_dir_for(target: Path, out_opt: str | None) -> Path:
    if out_opt:
        return Path(out_opt)
    return target.parent if target.is_file() else target / "脱敏结果"


def process_one(mode: str, path: Path, outdir: Path, assigner: Assigner,
                exclude: frozenset[str], use_ner: bool) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".pdf":
        if mode == "scan":
            edits, warnings = pdf_processor.scan_pdf(path, use_ner)
            items = [{
                "placeholder": assigner(e.span), "label": e.span.label,
                "original": e.span.text, "context": e.context,
                "location": f"第{e.page_no}页", "note": e.note,
            } for e in edits]
        else:
            out = outdir / f"{path.stem}{REDACTED_SUFFIX}.pdf"
            items, warnings, _n = pdf_processor.apply_pdf(
                path, out, assigner, exclude, use_ner)
            write_mapping(outdir / f"{path.stem}{REDACTED_SUFFIX}_映射表.json",
                          items, warnings)
    else:
        if mode == "scan":
            hits, warnings = docx_processor.scan_docx(path, use_ner)
            items = [{
                "placeholder": assigner(s), "label": s.label,
                "original": s.text,
                "context": docx_processor.context_of(docx_processor.para_text(h.para), s),
                "location": h.desc, "note": s.note,
            } for h in hits for s in h.spans]
        else:
            out = outdir / f"{path.stem}{REDACTED_SUFFIX}.docx"
            items, warnings, _n = docx_processor.apply_docx(
                path, out, assigner, exclude, use_ner)
            write_mapping(outdir / f"{path.stem}{REDACTED_SUFFIX}_映射表.json",
                          items, warnings)

    if mode == "scan":
        report = outdir / f"{path.stem}_脱敏审查.md"
        write_scan_report(report, path.name, items, warnings)
        return {"file": path.name, "ok": True, "count": len(items),
                "warnings": warnings, "outputs": [report.name]}

    write_scan_report(outdir / f"{path.stem}{REDACTED_SUFFIX}_报告.md",
                      path.name, items, warnings)
    names = {it["label"] for it in items}
    counts = Counter(it["label"] for it in items)
    detail = "，".join(f"{label_zh(k)} {counts[k]}" for k in sorted(counts))
    return {"file": path.name, "ok": True, "count": len(items),
            "warnings": warnings, "outputs": [out.name], "detail": detail,
            "labels": names}


def print_summary(results: list[dict], mode: str):
    print()
    ok = sum(1 for r in results if r["ok"])
    print(f"完成：{ok}/{len(results)} 个文件"
          + (f"，共 {sum(r['count'] for r in results)} 处" if mode == "apply" else ""))
    for r in results:
        if r["ok"]:
            line = f"  ✓ {r['file']}：{r['count']} 处"
            if r.get("detail"):
                line += f"（{r['detail']}）"
            print(line)
            for w in r["warnings"]:
                print(f"      ⚠ {w}")
        else:
            print(f"  ✗ {r['file']}：{r['error']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="合同脱敏：金额等敏感信息识别与真抹除")
    ap.add_argument("mode", choices=["scan", "apply"], help="scan=只识别出报告；apply=执行抹除")
    ap.add_argument("target", help="docx/pdf 文件，或包含它们的目录")
    ap.add_argument("-o", "--outdir", help="输出目录（缺省：文件旁 / 目录下 脱敏结果\\）")
    ap.add_argument("--exclude", help="白名单词库文件：一行一条原文，命中的不抹")
    ap.add_argument("--ner", action="store_true", help="启用 NER 识别人名/机构名（需 pip install hanlp）")
    args = ap.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        ap.error(f"路径不存在：{target}")
    files = collect_files(target)
    if not files:
        ap.error("目录下没有找到 .docx / .pdf 文件")
    print(f"{'识别' if args.mode == 'scan' else '抹除'} {len(files)} 个文件 → "
          f"{out_dir_for(target, args.outdir)}")

    exclude = load_exclude(args.exclude)
    assigner = Assigner()
    results = []
    for f in files:
        try:
            results.append(process_one(args.mode, f, out_dir_for(target, args.outdir),
                                       assigner, exclude, args.ner))
        except (DocxError, PdfError) as exc:
            results.append({"file": f.name, "ok": False, "error": str(exc)})
        except Exception as exc:  # 单文件失败不拖垮批次
            results.append({"file": f.name, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
    print_summary(results, args.mode)
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
