# -*- coding: utf-8 -*-
"""抓取网页里的合同附件（pdf/docx）直链并下载。"""
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = Path(__file__).resolve().parent / "real"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    return data if binary else data.decode("utf-8", errors="replace")


def fetch_page_attachments(page_url, tag):
    html = get(page_url)
    links = re.findall(r'href="([^"]+\.(?:pdf|docx?))"', html, re.I)
    if not links:
        print(f"  [{tag}] 页面无附件直链")
        return
    for link in links:
        if link.startswith("/"):
            base = re.match(r"(https?://[^/]+)", page_url).group(1)
            link = base + link
        elif not link.startswith("http"):
            link = page_url.rsplit("/", 1)[0] + "/" + link
        name = tag + "_" + Path(urllib.request.unquote(link)).name
        try:
            data = get(link, binary=True)
            (OUT / name).write_bytes(data)
            print(f"  [{tag}] {link} -> {name} ({len(data)} bytes)")
        except Exception as exc:
            print(f"  [{tag}] {link} 失败: {exc}")


if __name__ == "__main__":
    for url, tag in [
        ("http://beijing.customs.gov.cn/hhht_customs/566223/fdzdgknr31/zfcg93/4641664/6219056/index.html", "hhht"),
    ]:
        fetch_page_attachments(url, tag)
