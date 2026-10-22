#!/usr/bin/env python3
"""Leitner scheduler for the .learning/ notebook (stdlib only).

Usage:
  python leitner.py due   [--dir .learning] [--today YYYY-MM-DD] [--all]
  python leitner.py grade ID nho|mo|quen [--dir .learning] [--today YYYY-MM-DD]
  python leitner.py next-id C|M|Q [--dir .learning] [--today YYYY-MM-DD]

Entry format (written by /reflect):
  ### C-20261022-01 · Title
  - Hộp: 1 | Ôn lần tới: 2026-10-23 | Ôn lần cuối: —
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}  # box -> days until next review
FILES = ("concepts.md", "mistakes.md")
HEAD = re.compile(r"^### ([CMQ]-\d{8}-\d{2}) · (.+)$")
META = re.compile(r"^- Hộp: (\d) \| Ôn lần tới: (\S+) \| Ôn lần cuối: (.+)$")
GRADES = {"nho": 1, "good": 1, "mo": 0, "hard": 0, "quen": -1, "again": -1}


def entries(root):
    for name in FILES:
        path = root / name
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            h = HEAD.match(line)
            if h and i + 1 < len(lines):
                m = META.match(lines[i + 1])
                if m:
                    yield {"id": h[1], "title": h[2], "box": int(m[1]),
                           "next": m[2], "last": m[3], "file": name}


def cmd_due(root, today, show_all):
    items = list(entries(root))
    due = [e for e in items if show_all or e["next"] <= today]
    due.sort(key=lambda e: (e["box"], e["next"]))
    for e in due:
        print(f'{e["id"]}\tHộp {e["box"]}\tÔn lần tới {e["next"]}\t{e["file"]}\t{e["title"]}')
    boxes = {b: sum(e["box"] == b for e in items) for b in INTERVALS}
    print(f"# {len(due)} mục đến hạn / {len(items)} mục. Theo hộp: "
          + ", ".join(f"H{b}={n}" for b, n in boxes.items()))


def cmd_grade(root, today, entry_id, grade):
    delta = GRADES[grade]
    for name in FILES:
        path = root / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:  # keep original line endings
            lines = f.read().splitlines(keepends=True)
        for i, line in enumerate(lines):
            h = HEAD.match(line.rstrip("\r\n"))
            if h and h[1] == entry_id:
                meta = lines[i + 1].rstrip("\r\n")
                m = META.match(meta)
                box = 1 if delta < 0 else min(5, int(m[1]) + delta)
                nxt = dt.date.fromisoformat(today) + dt.timedelta(days=INTERVALS[box])
                eol = lines[i + 1][len(meta):]
                lines[i + 1] = f"- Hộp: {box} | Ôn lần tới: {nxt} | Ôn lần cuối: {today}{eol}"
                with path.open("w", encoding="utf-8", newline="") as f:
                    f.write("".join(lines))
                print(f"{entry_id}: Hộp {m[1]} -> {box}, ôn lần tới {nxt}")
                return
    sys.exit(f"Không tìm thấy {entry_id}")


def cmd_next_id(root, today, kind):
    stamp = today.replace("-", "")
    name = {"C": "concepts.md", "M": "mistakes.md", "Q": "open-questions.md"}[kind]
    path = root / name
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    used = [int(n) for n in re.findall(rf"^### {kind}-{stamp}-(\d{{2}})", text, re.M)]
    print(f"{kind}-{stamp}-{max(used, default=0) + 1:02d}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["due", "grade", "next-id"])
    p.add_argument("args", nargs="*")
    p.add_argument("--dir", default=".learning")
    p.add_argument("--today", default=dt.date.today().isoformat())
    p.add_argument("--all", action="store_true")
    a = p.parse_args()
    root = pathlib.Path(a.dir)
    if a.cmd == "due":
        cmd_due(root, a.today, a.all)
    elif a.cmd == "grade":
        if len(a.args) != 2 or a.args[1] not in GRADES:
            p.error("grade ID nho|mo|quen")
        cmd_grade(root, a.today, *a.args)
    else:
        if len(a.args) != 1 or a.args[0] not in "CMQ":
            p.error("next-id C|M|Q")
        cmd_next_id(root, a.today, a.args[0])


if __name__ == "__main__":
    main()
