#!/usr/bin/env python3
"""
A minimal Point & Figure (P&F) chart renderer.

Reads an OHLC CSV (columns: date,open,high,low,close), builds classic
X/O columns from intraday high/low movement, and renders the chart as
plain text (stdout) or a standalone HTML page.

This is a charting utility only - no signals, no indicators, no advice.

Usage:
    python pnf.py sample_ohlc.csv --box 100 --reversal 3 --html chart.html
    python pnf.py sample_ohlc.csv --box 100 --reversal 3   # text output
"""

import argparse
import html
import sys
from pathlib import Path

import csv


def load_ohlc(path: str):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "date": r["date"],
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
            })
    rows.sort(key=lambda x: x["date"])
    return rows


def build_columns(rows, box: float, reversal: int):
    """Return list of columns; each column is dict {dir: 'X'|'O', marks: [levels]}."""
    first = rows[0]["close"]
    direction = "X" if rows[0]["high"] >= first else "O"
    level = first
    columns = []
    col = {"dir": direction, "marks": []}

    def draw_x(start, end):
        lo = int(min(start, end) // box) + 1
        hi = int(max(start, end) // box)
        return list(range(lo, hi + 1))

    marks = draw_x(level, rows[0]["high"]) if direction == "X" \
        else draw_x(rows[0]["low"], level)
    col["marks"].extend(marks)
    level = rows[0]["high"] if direction == "X" else rows[0]["low"]

    for bar in rows[1:]:
        if direction == "X":
            target = bar["high"]
            if target >= (max(col["marks"]) + 1) * box:
                col["marks"].extend(draw_x(level, target))
                level = target
                continue
            if bar["low"] <= level - reversal * box:
                columns.append(col)
                direction = "O"
                col = {"dir": "O", "marks": draw_x(bar["low"], level - box)}
                level = bar["low"]
        else:
            target = bar["low"]
            if target <= (min(col["marks"]) - 1) * box:
                col["marks"].extend(draw_x(target, level))
                level = target
                continue
            if bar["high"] >= level + reversal * box:
                columns.append(col)
                direction = "X"
                col = {"dir": "X", "marks": draw_x(level + box, bar["high"])}
                level = bar["high"]
    columns.append(col)
    return columns


def render_text(columns, box):
    all_levels = [m for c in columns for m in c["marks"]]
    top, bottom = max(all_levels), min(all_levels)
    lines = []
    for lv in range(top, bottom - 1, -1):
        cells = []
        for c in columns:
            cells.append(c["dir"] if lv in c["marks"] else ".")
        lines.append(f"{lv * box:>10,.0f} | " + " ".join(cells))
    lines.append(" " * 11 + "+" + "-" * (2 * len(columns) - 1))
    return "\n".join(lines)


def render_html(columns, box, reversal, title):
    all_levels = [m for c in columns for m in c["marks"]]
    top, bottom = max(all_levels), min(all_levels)
    rows_html = []
    for lv in range(top, bottom - 1, -1):
        cells = []
        for c in columns:
            mark = c["dir"] if lv in c["marks"] else ""
            cls = "x" if c["dir"] == "X" else "o"
            cells.append(f'<td class="{cls}">{html.escape(mark)}</td>')
        rows_html.append(
            f'<tr><td class="lvl">{lv * box:,.0f}</td>' + "".join(cells) + "</tr>")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body {{ font-family: ui-monospace, Menlo, monospace; background:#fafafa; }}
table {{ border-collapse: collapse; }}
td {{ width: 18px; height: 18px; text-align: center; border-radius: 3px; }}
.x {{ color: #fff; background: #2b7de9; font-weight: 700; }}
.o {{ color: #fff; background: #e05252; font-weight: 700; }}
.lvl {{ width: 90px; text-align: right; padding-right: 8px; color: #555; }}
h2 {{ font-family: sans-serif; }}
</style></head><body>
<h2>{html.escape(title)} &nbsp;<small>(box={box}, reversal={reversal})</small></h2>
<table>{''.join(rows_html)}</table></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a Point & Figure chart from OHLC CSV.")
    ap.add_argument("csvfile", help="CSV with columns: date,open,high,low,close")
    ap.add_argument("--box", type=float, default=1.0, help="box size in price units")
    ap.add_argument("--reversal", type=int, default=3, help="reversal boxes (typically 3)")
    ap.add_argument("--html", metavar="FILE", help="also write a standalone HTML chart")
    args = ap.parse_args()

    if not Path(args.csvfile).exists():
        print(f"error: file not found: {args.csvfile}", file=sys.stderr)
        return 1

    rows = load_ohlc(args.csvfile)
    columns = build_columns(rows, args.box, args.reversal)
    print(render_text(columns, args.box))

    if args.html:
        Path(args.html).write_text(
            render_html(columns, args.box, args.reversal, args.csvfile))
        print(f"\nHTML chart written -> {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
