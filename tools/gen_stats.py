#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 math-of-li（笔记）与 exercises（习题）两个仓库读取学习数据，
生成 Profile README 用的 SVG 统计图。

用法:
    python tools/gen_stats.py \
        --notes <math-of-li 路径> \
        --exercises <exercises 路径> \
        --ref main --out assets

生成:
    assets/knowledge.svg     课程分布（笔记 ↔ 习题 对照）
    assets/contribution.svg  贡献概览卡片 + 月度提交柱状图

注意：
  · 行数必须按 UTF-8 解码后统计 —— PowerShell 5.1 的 `Get-Content` 默认 ANSI，
    会把 UTF-8 字节按 GBK 解码并吞掉部分换行，结果偏小约 15%。
  · 只统计 .md 文件；PDF/PNG 等二进制若被当文本读，会凭空产生几万"行"。
  · 数据源一律走 git 对象库（ls-tree + cat-file --batch），不扫工作区 ——
    OneDrive 同步会让目录间歇性不可见，工作区也可能有未提交的删除。
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- 课程元信息

# (显示名, 英文名, 主题色, math-of-li 中的目录, exercises 中的目录)
COURSES: list[tuple[str, str, str, str | None, str | None]] = [
    ("矩阵分析",   "Matrix Analysis",       "#1f6feb", "矩阵分析.md",   None),
    ("泛函分析",   "Functional Analysis",   "#8957e5", "泛函分析.md",   "泛函分析"),
    ("微分几何",   "Differential Geometry", "#2ea043", "微分几何.md",   "微分几何"),
    ("常微分方程", "ODE",                    "#d29922", "常微分复习.md", None),
    ("偏微分方程", "PDE",                    "#e3642a", "偏微分方程.md", None),
    ("复变函数",   "Complex Analysis",      "#db61a2", "复变函数复习.md", None),
    ("机器学习",   "Machine Learning",      "#0969da", None,           "机器学习"),
]

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',"
        "'PingFang SC','Microsoft YaHei',sans-serif")


@dataclass
class Course:
    name: str
    en: str
    color: str
    notes: int = 0        # 笔记篇数
    note_lines: int = 0   # 笔记行数
    ex: int = 0           # 习题篇数
    ex_lines: int = 0     # 习题行数

    @property
    def total_lines(self) -> int:
        return self.note_lines + self.ex_lines


@dataclass
class RepoStats:
    name: str
    commits: int = 0
    first: str = ""
    last: str = ""
    months: dict[str, int] = field(default_factory=dict)
    files: int = 0
    lines: int = 0

    @property
    def span(self) -> int:
        if not (self.first and self.last):
            return 0
        from datetime import date
        y1, m1, d1 = map(int, self.first.split("-"))
        y2, m2, d2 = map(int, self.last.split("-"))
        return (date(y2, m2, d2) - date(y1, m1, d1)).days + 1


# ---------------------------------------------------------------- git 读取

def run_git(repo: Path, *args: str) -> str:
    cmd = ["git", "-c", "core.quotepath=false", *args]
    res = subprocess.run(
        cmd, cwd=str(repo), capture_output=True,
        env={**os.environ, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"},
    )
    return res.stdout.decode("utf-8", "replace")


def read_blobs(repo: Path, paths: list[str], ref: str) -> dict[str, str]:
    """用 git cat-file --batch 一次性读取多个 blob。"""
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
        out[p] = data[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        pos = nl + 1 + size + 1
    return out


def count_lines(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def tracked_md(repo: Path, ref: str, subdir: str) -> list[str]:
    out = run_git(repo, "ls-tree", "-r", "--name-only", ref, "--", subdir)
    return [p for p in out.splitlines() if p.strip().lower().endswith(".md")]


def repo_meta(repo: Path, ref: str, name: str) -> RepoStats:
    s = RepoStats(name=name)
    log_ref = [] if ref == ":" else [ref]
    s.commits = len([l for l in run_git(repo, "log", *log_ref, "--oneline").splitlines() if l.strip()])
    dates = [l for l in run_git(repo, "log", *log_ref, "--pretty=format:%ad",
                                "--date=short").splitlines() if l.strip()]
    if dates:
        s.first, s.last = min(dates), max(dates)
        for d in dates:
            s.months[d[:7]] = s.months.get(d[:7], 0) + 1
        s.months = dict(sorted(s.months.items()))
    return s


# ---------------------------------------------------------------- 数据采集

def collect(notes_repo: Path, ex_repo: Path, ref: str) -> tuple[list[Course], RepoStats, RepoStats]:
    courses: list[Course] = []
    by_name: dict[str, Course] = {}
    for name, en, color, _ndir, _edir in COURSES:
        c = Course(name=name, en=en, color=color)
        courses.append(c)
        by_name[name] = c

    # ---- math-of-li：math.md/<课程>.md/*.md ----
    note_stats = repo_meta(notes_repo, ref, "math-of-li")
    note_files = tracked_md(notes_repo, ref, "math.md")
    note_stats.files = len(note_files)
    per_course: dict[str, list[str]] = {}
    for p in note_files:
        m = re.match(r"^math\.md/([^/]+)/", p)
        if m:
            per_course.setdefault(m.group(1), []).append(p)
    for name, _en, _c, ndir, _e in COURSES:
        if not ndir:
            continue
        paths = sorted(per_course.get(ndir, []))
        blobs = read_blobs(notes_repo, paths, ref)
        c = by_name[name]
        for p in paths:
            t = blobs.get(p)
            if t is None:
                continue
            c.notes += 1
            c.note_lines += count_lines(t)
            note_stats.lines += count_lines(t)

    # ---- exercises：<课程>/*.md（根目录 README 不计入课程）----
    ex_stats = repo_meta(ex_repo, ref, "exercises")
    ex_files = tracked_md(ex_repo, ref, ".")
    per_ex: dict[str, list[str]] = {}
    for p in ex_files:
        parts = p.split("/")
        if len(parts) >= 2:
            per_ex.setdefault(parts[0], []).append(p)
    ex_stats.files = sum(len(v) for v in per_ex.values())   # 只算课程内的习题，不含根目录 README
    for name, _en, _c, _n, edir in COURSES:
        if not edir:
            continue
        paths = sorted(per_ex.get(edir, []))
        blobs = read_blobs(ex_repo, paths, ref)
        c = by_name[name]
        for p in paths:
            t = blobs.get(p)
            if t is None:
                continue
            c.ex += 1
            c.ex_lines += count_lines(t)
            ex_stats.lines += count_lines(t)

    return courses, note_stats, ex_stats


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
  .dv {{ stroke:#d0d7de; }}
  text {{ font-family:{FONT}; }}
  @media (prefers-color-scheme: dark) {{
    .bg {{ fill:#0d1117; stroke:#30363d; }}
    .t  {{ fill:#e6edf3; }}
    .st {{ fill:#9198a1; }}
    .tr {{ fill:#e6edf3; opacity:.12; }}
    .dv {{ stroke:#30363d; }}
  }}
</style>
'''


# ---------------------------------------------------------------- 图 1：课程分布

def render_knowledge(courses: list[Course], ns: RepoStats, es: RepoStats, out: Path) -> None:
    rows = [c for c in courses if c.notes or c.ex]
    rowh, top = 50, 92
    w = 880
    h = top + rowh * len(rows) + 74

    x_name, x_bar, bar_w = 26, 152, 300
    x_note = 566
    x_ex = 680
    x_total = w - 26
    vmax = max((c.note_lines for c in rows), default=1)

    p = [svg_header(w, h, "课程分布：笔记与习题")]
    p.append(f'<rect class="bg" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12"/>')
    p.append('<text class="t" x="26" y="34" font-size="17" font-weight="600">📚 课程分布</text>')
    p.append(f'<text class="st" x="{w-26}" y="34" font-size="11.5" text-anchor="end">'
             f'笔记 {ns.files} 篇 · 习题 {es.files} 篇</text>')

    p.append('<text class="st" x="26" y="68" font-size="10.5">课程</text>')
    p.append(f'<text class="st" x="{x_note}" y="68" font-size="10.5" text-anchor="end">笔记</text>')
    p.append(f'<text class="st" x="{x_ex}" y="68" font-size="10.5" text-anchor="end">习题</text>')
    p.append(f'<text class="st" x="{x_total}" y="68" font-size="10.5" text-anchor="end">行数合计</text>')
    p.append(f'<line class="dv" x1="26" y1="76" x2="{w-26}" y2="76" stroke-width="1" opacity=".7"/>')

    for i, c in enumerate(rows):
        y = top + i * rowh
        cy = y + 22
        p.append(f'<text class="t" x="{x_name}" y="{cy}" font-size="13.5" font-weight="600">{esc(c.name)}</text>')
        p.append(f'<text class="st" x="{x_name}" y="{cy+15}" font-size="9.5">{esc(c.en)}</text>')

        p.append(f'<rect class="tr" x="{x_bar}" y="{cy-8}" width="{bar_w}" height="16" rx="8"/>')
        bw = max(0, round(bar_w * c.note_lines / vmax)) if c.note_lines else 0
        if bw > 0:
            p.append(f'<rect x="{x_bar}" y="{cy-8}" width="{max(6, bw)}" height="16" rx="8" '
                     f'fill="{c.color}" opacity="0.9"/>')
        # 习题段接在笔记条右侧
        if c.ex_lines:
            start = x_bar + min(bw, bar_w - 10)
            ebw = max(8, round(bar_w * c.ex_lines / vmax))
            p.append(f'<rect x="{start}" y="{cy-8}" width="{min(ebw, bar_w - (start - x_bar))}" '
                     f'height="16" rx="8" fill="{c.color}" opacity="0.32"/>')

        if c.notes:
            p.append(f'<text class="t" x="{x_note}" y="{cy+2}" font-size="11.5" font-weight="600" '
                     f'text-anchor="end">{c.notes}<tspan class="st" font-size="9.5" font-weight="400"> 篇</tspan></text>')
            p.append(f'<text class="st" x="{x_note}" y="{cy+16}" font-size="9.5" text-anchor="end">'
                     f'{c.note_lines:,}</text>')
        else:
            p.append(f'<text class="st" x="{x_note}" y="{cy+2}" font-size="11.5" text-anchor="end">—</text>')

        if c.ex:
            p.append(f'<text class="t" x="{x_ex}" y="{cy+2}" font-size="11.5" font-weight="600" '
                     f'text-anchor="end">{c.ex}<tspan class="st" font-size="9.5" font-weight="400"> 篇</tspan></text>')
            p.append(f'<text class="st" x="{x_ex}" y="{cy+16}" font-size="9.5" text-anchor="end">'
                     f'{c.ex_lines:,}</text>')
        else:
            p.append(f'<text class="st" x="{x_ex}" y="{cy+2}" font-size="11.5" text-anchor="end">—</text>')

        p.append(f'<text class="t" x="{x_total}" y="{cy+2}" font-size="12" font-weight="600" '
                 f'text-anchor="end">{c.total_lines:,}</text>')

    y = top + rowh * len(rows) + 10
    p.append(f'<line class="dv" x1="26" y1="{y}" x2="{w-26}" y2="{y}" stroke-width="1" opacity=".7"/>')
    tot_n = sum(c.notes for c in rows)
    tot_e = sum(c.ex for c in rows)
    p.append(f'<text class="st" x="26" y="{y+27}" font-size="11.5">'
             f'共 <tspan class="t" font-weight="700">{len(rows)}</tspan> 门课 · '
             f'笔记 <tspan class="t" font-weight="700">{tot_n}</tspan> 篇 / '
             f'<tspan class="t" font-weight="700">{sum(c.note_lines for c in rows):,}</tspan> 行 · '
             f'习题 <tspan class="t" font-weight="700">{tot_e}</tspan> 篇 / '
             f'<tspan class="t" font-weight="700">{sum(c.ex_lines for c in rows):,}</tspan> 行</text>')
    p.append('</svg>')
    out.write_text("\n".join(p), encoding="utf-8")
    print(f"[OK] {out}")


# ---------------------------------------------------------------- 图 2：贡献概览

def render_contribution(ns: RepoStats, es: RepoStats, courses: list[Course], out: Path) -> None:
    w, h = 880, 268
    tot_notes = sum(c.notes for c in courses)
    tot_ex = sum(c.ex for c in courses)

    cards = [
        ("笔记", f'{tot_notes}', "篇", "#1f6feb", f'{ns.lines:,} 行'),
        ("习题", f'{tot_ex}', "篇", "#8957e5", f'{es.lines:,} 行'),
        ("Git 提交", f'{ns.commits + es.commits}', "次", "#2ea043", "2 个仓库"),
        ("持续", f'{max(ns.span, es.span)}', "天", "#e3642a", f'{min(ns.first, es.first)} 起'),
    ]
    gap, pad, ch = 14, 22, 76
    cw = (w - pad * 2 - gap * 3) / 4

    p = [svg_header(w, h, "贡献概览")]
    p.append(f'<rect class="bg" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12"/>')
    p.append('<text class="t" x="22" y="34" font-size="17" font-weight="600">📈 贡献概览</text>')
    p.append(f'<text class="st" x="{w-22}" y="34" font-size="11.5" text-anchor="end">'
             f'{min(ns.first, es.first)} → {max(ns.last, es.last)}</text>')

    for i, (label, value, unit, color, sub) in enumerate(cards):
        x = pad + i * (cw + gap)
        y = 48
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="10" fill="{color}" opacity="0.08"/>')
        p.append(f'<rect x="{x:.1f}" y="{y}" width="3.5" height="{ch}" rx="1.75" fill="{color}"/>')
        p.append(f'<text class="st" x="{x+14:.1f}" y="{y+21}" font-size="11">{esc(label)}</text>')
        p.append(f'<text x="{x+14:.1f}" y="{y+49}" font-size="23" font-weight="700" fill="{color}">'
                 f'{esc(value)}<tspan font-size="11.5" font-weight="500" dx="3">{esc(unit)}</tspan></text>')
        p.append(f'<text class="st" x="{x+14:.1f}" y="{y+66}" font-size="9.5">{esc(sub)}</text>')

    # ---- 月度提交（两仓库叠加）----
    y0 = 168
    p.append(f'<line class="dv" x1="{pad}" y1="{y0-30}" x2="{w-pad}" y2="{y0-30}" stroke-width="1" opacity=".7"/>')
    p.append(f'<text class="st" x="{pad}" y="{y0-13}" font-size="11.5">月度提交</text>')
    p.append(f'<text class="st" x="{w-pad}" y="{y0-13}" font-size="10" text-anchor="end">'
             f'<tspan fill="#1f6feb">■</tspan> math-of-li  '
             f'<tspan fill="#8957e5">■</tspan> exercises</text>')

    months = sorted(set(ns.months) | set(es.months))
    if months:
        area_x, area_w = pad, w - pad * 2
        slot = area_w / len(months)
        bw = min(50.0, slot * 0.5)
        base = h - 42
        full = 46.0
        vmax = max(max(ns.months.get(m, 0), es.months.get(m, 0)) for m in months) or 1
        for i, m in enumerate(months):
            x = area_x + i * slot + (slot - bw) / 2
            n, e = ns.months.get(m, 0), es.months.get(m, 0)
            hn = full * n / vmax
            he = full * e / vmax
            if hn > 0:
                p.append(f'<rect x="{x:.1f}" y="{base-hn:.1f}" width="{bw:.1f}" height="{hn:.1f}" '
                         f'rx="3" fill="#1f6feb" opacity=".85"/>')
            if he > 0:
                p.append(f'<rect x="{x:.1f}" y="{base-hn-he:.1f}" width="{bw:.1f}" height="{he:.1f}" '
                         f'rx="3" fill="#8957e5" opacity=".85"/>')
            total = n + e
            if total:
                p.append(f'<text class="st" x="{x+bw/2:.1f}" y="{base-hn-he-6:.1f}" font-size="10" '
                         f'text-anchor="middle">{total}</text>')
            p.append(f'<text class="st" x="{x+bw/2:.1f}" y="{base+16:.1f}" font-size="10" '
                     f'text-anchor="middle">{m[5:].lstrip("0")}月</text>')

    p.append('</svg>')
    out.write_text("\n".join(p), encoding="utf-8")
    print(f"[OK] {out}")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", required=True, help="math-of-li 仓库路径")
    ap.add_argument("--exercises", required=True, help="exercises 仓库路径")
    ap.add_argument("--ref", default="HEAD", help="git ref（分支/标签/提交）")
    ap.add_argument("--out", default="assets", help="SVG 输出目录")
    a = ap.parse_args()

    notes_repo = Path(a.notes).resolve()
    ex_repo = Path(a.exercises).resolve()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    courses, ns, es = collect(notes_repo, ex_repo, a.ref)

    print(f"[math-of-li] {ns.files} 个文件 · {ns.lines:,} 行 · {ns.commits} 次提交 · "
          f"{ns.first} -> {ns.last}（{ns.span} 天）")
    print(f"[exercises] {es.files} 个文件 · {es.lines:,} 行 · {es.commits} 次提交 · "
          f"{es.first} -> {es.last}（{es.span} 天）")
    print()
    for c in courses:
        if c.notes or c.ex:
            print(f"  {c.name:<10} 笔记 {c.notes:>3} 篇/{c.note_lines:>6,} 行    "
                  f"习题 {c.ex:>2} 篇/{c.ex_lines:>5,} 行    合计 {c.total_lines:>6,} 行")

    render_knowledge(courses, ns, es, out / "knowledge.svg")
    render_contribution(ns, es, courses, out / "contribution.svg")


if __name__ == "__main__":
    main()
