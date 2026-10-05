# -*- coding: utf-8 -*-
"""从 GitHub 仓库下载真实合同样本文件。"""
import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = Path(__file__).resolve().parent / "real"
OUT.mkdir(parents=True, exist_ok=True)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "test"})
    return urllib.request.urlopen(req, timeout=60).read()


repo = "xiaodingfeng/contract-review-v2"
tree = json.loads(get(f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1"))
files = [n for n in tree["tree"]
         if n["type"] == "blob" and n["path"].lower().endswith((".docx", ".pdf", ".doc"))]
print(f"仓库 {repo} 中共 {len(files)} 个文档文件")
for n in files[:20]:
    print(f"  {n['size']:>9}  {n['path']}")
    if n["size"] > 0:
        try:
            data = get(f"https://raw.githubusercontent.com/{repo}/master/{urllib.request.quote(n['path'])}")
            dest = OUT / Path(n["path"]).name
            dest.write_bytes(data)
            print(f"    -> 已下载 {dest.name} ({len(data)} bytes)")
        except Exception as exc:
            print(f"    -> 失败: {exc}")
