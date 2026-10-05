# -*- coding: utf-8 -*-
"""抽取 index.html 的 <script> 做语法检查（node --check）。"""
import io
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
html = io.open(Path(__file__).resolve().parents[1] / "gui" / "index.html", encoding="utf-8").read()
script = html.split("<script>")[1].split("</script>")[0]
Path(__file__).with_name("_check.js").write_text(script, encoding="utf-8")
r = subprocess.run([r"C:\Program Files\nodejs\node.exe", "--check", str(Path(__file__).with_name("_check.js"))],
                   capture_output=True, text=True)
print("syntax:", "OK" if r.returncode == 0 else "FAIL")
if r.returncode:
    print(r.stderr)
sys.exit(r.returncode)
