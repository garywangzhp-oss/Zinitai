# -*- coding: utf-8 -*-
"""抓取政府页面上的合同附件直链并下载（多个候选页面，成功即止）。"""
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = Path(__file__).resolve().parent / "real"
OUT.mkdir(parents=True, exist_ok=True)
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

PAGES = [
    ("https://jnhrss.jinan.gov.cn/col18780/art/2025/art_18780_4807010.html", "jinan_ldht"),
    ("https://hrss.henan.gov.cn/2023/04-17/2726489.html", "henan_ldht"),
]


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    return data if binary else data.decode("utf-8", errors="replace")


for page_url, tag in PAGES:
    print(f"== {page_url}")
    try:
        html = get(page_url)
    except Exception as exc:
        print(f"  页面获取失败: {exc}")
        continue
    print(f"  页面 {len(html)} 字符")
    links = re.findall(r'href=["\']([^"\']+\.(?:pdf|docx?))(?:\?[^"\']*)?["\']', html, re.I)
    if not links:
        # 有些政府站用 onclick 或 data 属性挂附件
        links = re.findall(r'["\']([^"\']+/(?:attach|file|upload)[^"\']+\.(?:pdf|docx?))["\']', html, re.I)
    print(f"  附件链接 {len(links)} 个")
    for link in links:
        if link.startswith("/"):
            base = re.match(r"(https?://[^/]+)", page_url).group(1)
            link = base + link
        elif not link.startswith("http"):
            link = page_url.rsplit("/", 1)[0] + "/" + link
        name = tag + "_" + Path(urllib.request.unquote(link.split("/")[-1].split("?")[0])).name
        try:
            data = get(link, binary=True)
            if len(data) < 200:
                print(f"  跳过过小文件 {name} ({len(data)})")
                continue
            (OUT / name).write_bytes(data)
            print(f"  ✓ {name} ({len(data)} bytes) <- {link}")
        except Exception as exc:
            print(f"  ✗ {link}: {exc}")
