# -*- coding: utf-8 -*-
"""对比渲染：脱敏稿 vs 还原稿，并打印关键文本的坐标。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pymupdf

red = pymupdf.open("tests/out/示例服务合同_脱敏.pdf")
res = pymupdf.open("tests/out/示例服务合同_还原.pdf")

print("== 脱敏稿中占位符坐标 ==")
for r in red[0].search_for("[金额#1]")[:3]:
    print("  [金额#1] rect:", r)
print("== 还原稿中原文坐标 ==")
for r in res[0].search_for("叁拾伍万元整")[:3]:
    print("  叁拾伍万元整 rect:", r)
for r in res[0].search_for("￥350,000.00")[:3]:
    print("  ￥350,000.00 rect:", r)

res[0].get_pixmap(dpi=110).save("tests/out/restore_check.png")
red[0].get_pixmap(dpi=110).save("tests/out/redacted_check.png")
print("已渲染 restore_check.png / redacted_check.png")
