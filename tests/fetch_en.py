# -*- coding: utf-8 -*-
"""在几个合同模板仓库里找 docx/pdf 文件并下载。"""
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


repos = ["Bonterms/Mutual-NDA", "cure53/Contracts", "mgifford/non-disclosure-agreements"]
for repo in repos:
    try:
        info = json.loads(get(f"https://api.github.com/repos/{repo}"))
        branch = info.get("default_branch", "main")
        tree = json.loads(get(f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"))
        files = [n for n in tree.get("tree", [])
                 if n["type"] == "blob" and n["path"].lower().endswith((".docx", ".pdf"))]
        print(f"== {repo} ({branch}): {len(files)} 个 docx/pdf")
        for n in files[:6]:
            print("   ", n["size"], n["path"])
            if n["size"] > 1000:
                try:
                    data = get(f"https://raw.githubusercontent.com/{repo}/{branch}/"
                               + urllib.request.quote(n["path"]))
                    dest = OUT / ("en_" + Path(n["path"]).name)
                    dest.write_bytes(data)
                    print(f"    -> {dest.name} ({len(data)} bytes)")
                except Exception as exc:
                    print("    -> 下载失败:", exc)
    except Exception as exc:
        print(f"== {repo}: 失败 {exc}")
