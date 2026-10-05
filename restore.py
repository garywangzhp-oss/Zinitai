"""还原：把脱敏稿里的占位符按映射表换回原文。

    python restore.py 脱敏文件 [更多脱敏文件...] [-o 输出目录]

映射表默认取文件同目录的 `{文件名}_映射表.json`（apply 时自动生成）；
输出为同目录下 `{文件名去_脱敏}_还原.{docx|pdf}`。

诚实声明：docx 逐字回填、格式保留；PDF 用与抹除相同的 redaction 机制
原位回填原文——内容可还原，但字体度量不保留，版式可能与原件有细微差异。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from processors import docx_processor, pdf_processor  # noqa: E402
from review.report import load_mapping_dict, pair_mapping  # noqa: E402


def restore_one(path: Path, outdir: Path | None) -> dict:
    mp = pair_mapping(path)
    if not mp:
        return {"name": path.name, "ok": False,
                "error": f"未找到映射表（应为 {path.stem}_映射表.json）"}
    mapping = load_mapping_dict(mp)
    out_stem = path.stem.replace("_脱敏", "_还原")
    out = (outdir or path.parent) / f"{out_stem}{path.suffix.lower()}"
    try:
        if path.suffix.lower() == ".pdf":
            n = pdf_processor.restore_pdf(str(path), str(out), mapping)
        else:
            n = docx_processor.restore_docx(str(path), str(out), mapping)
        return {"name": path.name, "out": str(out), "count": n, "ok": True,
                "mapping": str(mp)}
    except Exception as exc:
        return {"name": path.name, "ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="还原：占位符按映射表换回原文")
    ap.add_argument("files", nargs="+", help="脱敏文件（_脱敏.docx / _脱敏.pdf）")
    ap.add_argument("-o", "--outdir", help="输出目录（缺省：与脱敏文件同目录）")
    args = ap.parse_args(argv)

    ok = 0
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"  ✗ {p.name}：文件不存在")
            continue
        r = restore_one(p, Path(args.outdir) if args.outdir else None)
        if r["ok"]:
            ok += 1
            print(f"  ✓ {r['name']} → {r['out']}（还原 {r['count']} 处）")
        else:
            print(f"  ✗ {r['name']}：{r['error']}")
    print(f"完成：{ok}/{len(args.files)}")
    return 0 if ok == len(args.files) else 1


if __name__ == "__main__":
    sys.exit(main())
