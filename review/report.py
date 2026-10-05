from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from detectors.base import label_zh


def write_scan_report(path_md, file_display, items, warnings, extra_note=""):
    """scan 的 Markdown 审查报告：给人过目，apply 阶段不读它。"""
    lines = [
        f"# 脱敏审查报告：{file_display}",
        "",
        f"- 生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
        f"- 命中：{len(items)} 处",
    ]
    if warnings:
        lines += [f"- ⚠ 警告：{w}" for w in warnings]
    if extra_note:
        lines.append(f"- {extra_note}")
    lines += ["", "| # | 类型 | 位置 | 原文 | 上下文 | 备注 |", "|---|---|---|---|---|---|"]
    for i, it in enumerate(items, 1):
        lines.append(
            f"| {i} | {label_zh(it['label'])} | {it['location']} "
            f"| `{it['original']}` | {it['context'].replace('|', '∣')} "
            f"| {it['note'] or ''} |"
        )
    lines += ["", "> 误报排除方式：把原文加入词库文件，`apply --exclude 词库.txt` 跳过。"]
    path_md.write_text("\n".join(lines), encoding="utf-8")


def write_mapping(path_json, items, warnings):
    """映射表：占位符 ↔ 原文。apply 的产物，也是还原功能的接口。"""
    path_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "warnings": warnings,
                "items": items,
            },
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )


def pair_mapping(file_path):
    """脱敏文件 → 同目录同名映射表；不存在返回 None。"""
    p = Path(file_path)
    mp = p.parent / f"{p.stem}_映射表.json"
    return mp if mp.exists() else None


def load_mapping_dict(path):
    """映射表 json → {占位符: 原文}。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {it["placeholder"]: it["original"] for it in data["items"]}
