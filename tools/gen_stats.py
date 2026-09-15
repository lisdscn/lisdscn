#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 math-of-li 仓库读取学习数据，生成 Profile README 用的 SVG 统计图。

用法:
    python tools/gen_stats.py --repo <math-of-li 路径> [--out assets]

生成:
    assets/knowledge.svg    知识分布（按课程篇数 / 行数）
    assets/contribution.svg 贡献概览卡片 + 月度活跃度

注意：行数必须用 UTF-8 解码后统计。PowerShell 5.1 的 `Get-Content`（默认 ANSI）
会把 UTF-8 字节按 GBK 解码，吞掉部分换行，导致行数统计偏小约 15%。
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------- 课程元信息

# 目录名 -> (显示名, 英文名, 主题色, 图标形状提示)
COURSES: dict[str, tuple[str, str, str]] = {
    "矩阵分析.md": ("矩阵分析", "Matrix Analysis", "#1f6feb"),
    "泛函分析.md": ("泛函分析", "Functional Analysis", "#8957e5"),
    "微分几何.md": ("微分几何", "Differential Geometry", "#2ea043"),
    "常微分复习.md": ("常微分方程", "ODE", "#d29922"),
    "偏微分方程.md": ("偏微分方程", "PDE", "#e3642a"),
    "复变函数复习.md": ("复变函数", "Complex Analysis", "#db61a2"),
}

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',"
        "'PingFang SC','Microsoft YaHei',sans-serif")
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"


@dataclass
class Course:
    key: str
    name: str
    en: str
    color: str
    notes: int = 0        # 笔记篇数
    lines: int = 0        # 当前总行数
    added: int = 0        # git 累计新增行数


# ---------------------------------------------------------------- 数据采集

def run_git(repo: Path, *args: str) -> str:
    """执行 git 命令，强制 UTF-8 且不转义中文路径。"""
    cmd = ["git", "-c", "core.quotepath=false", *args]
    res = subprocess.run(
        cmd, cwd=str(repo), capture_output=True,
        env={**os.environ, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"},
    )
    return res.stdout.decode("utf-8", "replace")


def read_blobs(repo: Path, paths: list[str], ref: str = ":") -> dict[str, str]:
    """用 git cat-file --batch 一次性读取多个 blob（默认从索引，不依赖工作区）。"""
    if not paths:
        return {}
    prefix = "" if ref == ":" else f"{ref}:"
    stdin = "".join(f"{prefix}{p}\n" for p in paths).encode("utf-8")
    res = subprocess.run(["git", "cat-file", "--batch"], cwd=str(repo),
                         input=stdin, capture_output=True)
    data, out, pos = res.stdout, {}, 0
    for p in paths:
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        header = data[pos:nl].decode("utf-8", "replace")
        if header.endswith(" missing") or " " not in header:
            pos = nl + 1
            continue
        try:
            size = int(header.rsplit(" ", 1)[1])
        except ValueError:
            pos = nl + 1
            continue
        start = nl + 1
        out[p] = data[start:start + size].decode("utf-8", "replace")
        pos = start + size + 1
    return out


def collect(repo: Path, ref: str = ":") -> tuple[list[Course], dict]:
    """扫描仓库，返回课程统计与全局统计。

    · ref=":" 表示 git 索引（工作区已暂存状态）；否则为分支/提交名
    · 内容取自 git 对象库，不受 OneDrive 同步、工作区未提交删除的影响
    · 行数按 UTF-8 解码后统计（PowerShell 默认 ANSI 会吞换行）
    """
    if ref == ":":
        tracked = [p for p in run_git(repo, "ls-files", "--", "math.md").splitlines()
                   if p.strip().lower().endswith(".md")]
    else:
        tracked = [p for p in run_git(repo, "ls-tree", "-r", "--name-only", ref,
                                      "--", "math.md").splitlines()
                   if p.strip().lower().endswith(".md")]
    if not tracked:
        sys.exit(f"[错误] {ref} 下没有 math.md/**.md，请确认 --repo / --ref")

    by_course: dict[str, list[str]] = {}
    for p in tracked:
        m = re.match(r"^math\.md/([^/]+)/", p)
        if m:
            by_course.setdefault(m.group(1), []).append(p)

    courses: list[Course] = []
    for dirname, (name, en, color) in COURSES.items():
        c = Course(key=dirname, name=name, en=en, color=color)
        paths = sorted(by_course.get(dirname, []))
        if not paths:
            print(f"[警告] {ref} 下未找到课程目录: {dirname}", file=sys.stderr)
        blobs = read_blobs(repo, paths, ref)
        for p in paths:
            text = blobs.get(p)
            if text is None:
                continue
            c.notes += 1
            c.lines += text.count("\n") + (0 if text.endswith("\n") else 1)
        courses.append(c)

    # git 累计新增行：按课程目录聚合
    by_key = {c.key: c for c in courses}
    log_ref = [] if ref == ":" else [ref]
    numstat = run_git(repo, "log", *log_ref, "--numstat", "--pretty=format:@@")
    for line in numstat.splitlines():
        m = re.match(r"^(\d+|-)\s+(\d+|-)\s+(.+)$", line)
        if not m or m.group(1) == "-":
            continue
        added = int(m.group(1))
        path = m.group(3).strip()
        mm = re.search(r"math\.md/([^/]+)/", path)
        if mm and mm.group(1) in by_key:
            by_key[mm.group(1)].added += added

    commits = len([l for l in run_git(repo, "log", *log_ref, "--oneline").splitlines() if l.strip()])
    dates = [l for l in run_git(repo, "log", *log_ref, "--pretty=format:%ad",
                               "--date=short").splitlines() if l.strip()]
    first, last = (min(dates), max(dates)) if dates else ("", "")

    # 月度提交活跃度
    months: dict[str, int] = {}
    for d in dates:
        months[d[:7]] = months.get(d[:7], 0) + 1
    months = dict(sorted(months.items()))

    from datetime import date
    span = 0
    if first and last:
        y1, m1, d1 = map(int, first.split("-"))
        y2, m2, d2 = map(int, last.split("-"))
        span = (date(y2, m2, d2) - date(y1, m1, d1)).days + 1

    total_added = sum(c.added for c in courses)
    stats = {
        "commits": commits,
        "first": first,
        "last": last,
        "span": span,
        "months": months,
        "courses": len([c for c in courses if c.notes]),
        "notes": sum(c.notes for c in courses),
        "lines": sum(c.lines for c in courses),
        "added": total_added,
    }
    return courses, stats


# ---------------------------------------------------------------- SVG 工具

def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def svg_header(w: int, h: int, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
  .bg {{ fill:#ffffff; stroke:#d0d7de; }}
  .t  {{ fill:#1f2328; }}
  .st {{ fill:#59636e; }}
  .tr {{ fill:#1f2328; opacity:.06; }}
  .mono {{ font-family:{MONO}; }}
  text {{ font-family:{FONT}; }}
  @media (prefers-color-scheme: dark) {{
    .bg {{ fill:#0d1117; stroke:#30363d; }}
    .t  {{ fill:#e6edf3; }}
    .st {{ fill:#9198a1; }}
    .tr {{ fill:#e6edf3; opacity:.12; }}
  }}
</style>
'''


# ---------------------------------------------------------------- 图 1：知识分布

def render_knowledge(courses: list[Course], stats: dict, out: Path) -> None:
    rows = [c for c in courses if c.notes]
    rowh, top = 48, 76
    w = 880
    h = top + rowh * len(rows) + 64
    bar_x, bar_w = 160, 458
    right_x = w - 26
    vmax = max(c.lines for c in rows)

    p = [svg_header(w, h, "知识分布 Knowledge Map")]
    p.append(f'<rect class="bg" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12"/>')
    p.append(f'<text class="t" x="26" y="40" font-size="17" font-weight="600">📚 知识分布</text>')
    p.append(f'<text class="st" x="{w-26}" y="40" font-size="12" text-anchor="end">'
             f'{stats["courses"]} 门课 · {stats["notes"]} 篇 · {stats["lines"]:,} 行</text>')
    p.append(f'<line x1="26" y1="56" x2="{w-26}" y2="56" stroke="#d0d7de" stroke-width="1" opacity=".6"/>')

    for i, c in enumerate(rows):
        y = top + i * rowh
        cy = y + 20
        # 课程名 + 英文名
        p.append(f'<text class="t" x="26" y="{cy}" font-size="13.5" font-weight="600">{esc(c.name)}</text>')
        p.append(f'<text class="st" x="26" y="{cy+15}" font-size="10">{esc(c.en)}</text>')
        # 轨道
        p.append(f'<rect class="tr" x="{bar_x}" y="{cy-8}" width="{bar_w}" height="16" rx="8"/>')
        # 进度条（按行数）
        bw = max(6, round(bar_w * c.lines / vmax))
        p.append(f'<rect x="{bar_x}" y="{cy-8}" width="{bw}" height="16" rx="8" fill="{c.color}" opacity="0.9"/>')
        if bw >= 74:
            p.append(f'<text x="{bar_x+bw-10}" y="{cy+3.5}" font-size="10" font-weight="700" '
                     f'text-anchor="end" fill="#ffffff">{c.lines:,} 行</text>')
        elif bw >= 34:
            p.append(f'<text x="{bar_x+bw+8}" y="{cy+4}" font-size="10.5" font-weight="700" '
                     f'fill="{c.color}">{c.lines:,} 行</text>')
        # 右侧：篇数
        p.append(f'<text class="t" x="{right_x}" y="{cy+4}" font-size="12" font-weight="700" '
                 f'text-anchor="end">{c.notes}<tspan class="st" font-size="10.5" font-weight="400"> 篇</tspan></text>')
        if bw < 34:
            p.append(f'<text class="st" x="{right_x}" y="{cy+17}" font-size="9.5" text-anchor="end" '
                     f'>{c.lines:,} 行</text>')

    # 汇总条
    y = top + rowh * len(rows) + 10
    p.append(f'<line x1="26" y1="{y}" x2="{w-26}" y2="{y}" stroke="#d0d7de" stroke-width="1" opacity=".6"/>')
    p.append(f'<text class="st" x="26" y="{y+27}" font-size="11.5">'
             f'{stats["notes"]} 篇笔记共 <tspan class="t" font-weight="700">{stats["lines"]:,}</tspan> 行 · '
             f'<tspan class="t" font-weight="700">{stats["commits"]}</tspan> 次提交 · 累计新增 '
             f'<tspan class="t" font-weight="700">{stats["added"]:,}</tspan> 行</text>')
    p.append('</svg>')
    out.write_text("\n".join(p), encoding="utf-8")
    print(f"[√] {out}")


# ---------------------------------------------------------------- 图 2：贡献卡片

def render_contribution(stats: dict, courses: list[Course], out: Path) -> None:
    months = list(stats["months"].items())
    w, h = 880, 250
    cards = [
        ("笔记篇数", f'{stats["notes"]}', "篇", "#1f6feb"),
        ("手写行数", f'{stats["lines"]:,}', "行", "#2ea043"),
        ("Git 提交", f'{stats["commits"]}', "次", "#8957e5"),
        ("持续时长", f'{stats["span"]}', "天", "#e3642a"),
    ]
    gap, pad = 14, 22
    cw = (w - pad * 2 - gap * 3) / 4
    ch = 72

    p = [svg_header(w, h, "贡献概览 Contribution")]
    p.append(f'<rect class="bg" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12"/>')
    p.append(f'<text class="t" x="{pad}" y="33" font-size="16" font-weight="600">📈 贡献概览</text>')
    p.append(f'<text class="st" x="{w-pad}" y="33" font-size="11.5" text-anchor="end">'
             f'{stats["first"]} → {stats["last"]}</text>')

    for i, (label, value, unit, color) in enumerate(cards):
        x = pad + i * (cw + gap)
        y = 46
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="10" '
                 f'fill="{color}" opacity="0.08"/>')
        p.append(f'<rect x="{x:.1f}" y="{y}" width="3.5" height="{ch}" rx="1.75" fill="{color}"/>')
        p.append(f'<text class="st" x="{x+14:.1f}" y="{y+22}" font-size="11">{esc(label)}</text>')
        p.append(f'<text x="{x+14:.1f}" y="{y+51}" font-size="23" font-weight="700" fill="{color}">'
                 f'{esc(value)}<tspan font-size="11.5" font-weight="500" dx="3">{esc(unit)}</tspan></text>')

    # ---- 月度活跃度 ----
    y0 = 148
    p.append(f'<line x1="{pad}" y1="{y0-26}" x2="{w-pad}" y2="{y0-26}" stroke="#d0d7de" stroke-width="1" opacity=".6"/>')
    p.append(f'<text class="st" x="{pad}" y="{y0-9}" font-size="11.5">月度提交活跃度</text>')

    if months:
        maxc = max(v for _, v in months)
        area_x, area_w = pad, w - pad * 2
        slot = area_w / len(months)
        bw = min(46.0, slot * 0.55)
        base = h - 34
        full = 58.0
        for i, (m, v) in enumerate(months):
            bh = max(3.0, full * v / maxc)
            x = area_x + i * slot + (slot - bw) / 2
            y = base - bh
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" '
                     f'fill="#1f6feb" opacity="{0.35 + 0.55*v/maxc:.2f}"/>')
            p.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" font-size="10.5" font-weight="600" '
                     f'text-anchor="middle" fill="#1f6feb">{v}</text>')
            p.append(f'<text class="st" x="{x+bw/2:.1f}" y="{base+16:.1f}" font-size="10" '
                     f'text-anchor="middle">{m[5:]}月</text>')

    p.append('</svg>')
    out.write_text("\n".join(p), encoding="utf-8")
    print(f"[√] {out}")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="math-of-li 仓库路径")
    ap.add_argument("--ref", default=":", help="git ref（分支/标签/提交），默认 : 即索引")
    ap.add_argument("--out", default="assets", help="SVG 输出目录")
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    courses, stats = collect(repo, a.ref)
    print(f"[ref] {a.ref}")
    for c in courses:
        if c.notes:
            print(f"  {c.name:<8} {c.notes:>3} 篇  {c.lines:>6,} 行  +{c.added:>6,} 行")

    render_knowledge(courses, stats, out / "knowledge.svg")
    render_contribution(stats, courses, out / "contribution.svg")

    # 供 README 手写数字使用
    print("\n[摘要]", {k: v for k, v in stats.items()})


if __name__ == "__main__":
    main()
