# -*- coding: utf-8 -*-
"""验证 PDF 的“真删除”：敏感原文是否真的从内容流消失（而非只被白块遮住）。

方法：PDF 正文用 CID 十六进制编码（如 <6280672f...>），ASCII 搜索无效。
这里用同一 china-s 字体渲染探针，拿到某个字符串的 CID 字节，再在
「原件 / 脱敏件」的解码内容流里精确比对：

  - 原件内容流：应含每个敏感串的 CID
  - 脱敏件内容流：应不含任何敏感串 CID，且应含占位符 CID

注意：探针 CID 只在原文与探针使用同一字体（本仓库 make_samples 生成的
china-s 样本、以及本工具自己产出的 PDF）时可比对；外部合同换字体后
CID 不同，此脚本不适用（那类用 get_text() + 独立提取器验证）。

用法：python tests/verify_pdf_deletion.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pymupdf as fitz  # noqa: E402

from detectors.base import placeholder_for  # noqa: E402
from processors import pdf_processor  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tests" / "samples" / "示例服务合同.pdf"
OUT = ROOT / "tests" / "out" / "_verify_deletion.pdf"


class Assigner:
    """同批内相同 (类型, 原文) 共享占位符编号（与 main.py / gui 一致）。"""

    def __init__(self):
        self.seq: dict = {}
        self.cache: dict = {}

    def __call__(self, span):
        key = (span.label, span.text)
        if key not in self.cache:
            self.seq[span.label] = self.seq.get(span.label, 0) + 1
            self.cache[key] = placeholder_for(span.label, self.seq[span.label])
        return self.cache[key]


def _hex_tokens(s):
    return "".join(re.sub(r"\s+", "", t).upper()
                   for t in re.findall(r"<([0-9A-Fa-f\s]+)>", s))


def cid_bytes(needle):
    """用同一 china-s 字体渲染 needle，返回其 CID 十六进制串。"""
    probe = fitz.open()
    page = probe.new_page()
    page.insert_text((72, 100), needle, fontname="china-s", fontsize=11)
    stream = page.read_contents().decode("latin-1", "replace")
    probe.close()
    return _hex_tokens(stream)


def decoded_streams(path):
    doc = fitz.open(path)
    parts = []
    for x in range(1, doc.xref_length()):
        try:
            b = doc.xref_stream(x)
        except Exception:
            continue
        if b:
            parts.append(b)
    doc.close()
    return _hex_tokens(b"\n".join(parts).decode("latin-1", "replace"))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    items, _warnings, _n = pdf_processor.apply_pdf(str(SRC), str(OUT), Assigner())
    needles = [it["original"] for it in items]
    placeholders = [it["placeholder"] for it in items]
    print(f"命中 {len(needles)} 处，占位符 {len(placeholders)} 个")

    src_blob = decoded_streams(SRC)
    red_blob = decoded_streams(OUT)
    fail = False

    print("\n敏感原文（原件应有 CID / 脱敏件应无）")
    for n in needles:
        cid = cid_bytes(n)
        in_src, in_red = cid in src_blob, cid in red_blob
        flag = "✓" if (in_src and not in_red) else "✗"
        print(f"  {flag} {n:<22} 原件CID={in_src}  脱敏件CID={in_red}")
        if not (in_src and not in_red):
            fail = True

    print("\n占位符（脱敏件应有 CID）")
    for ph in placeholders:
        cid = cid_bytes(ph)
        in_red = cid in red_blob
        flag = "✓" if in_red else "✗"
        print(f"  {flag} {ph:<22} 脱敏件CID={in_red}")
        if not in_red:
            fail = True

    text = "\n".join(p.get_text() for p in fitz.open(OUT))
    leaked = [n for n in needles if n in text]
    print(f"\n文本层残留原文：{leaked or '无'}")
    if leaked:
        fail = True

    print("RESULT:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())