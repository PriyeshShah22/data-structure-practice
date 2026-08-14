#!/usr/bin/env python3
"""Generate a GitHub-style SVG heatmap from public Codeforces submissions."""

from __future__ import annotations

import argparse
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo


API_URL = "https://codeforces.com/api/user.status"
DEFAULT_HANDLE = "codingwps"
DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_OUTPUT = Path("assets/codeforces-heatmap.svg")


def fetch_submissions(handle: str, attempts: int = 3) -> list[dict]:
    """Return the public submission history for a Codeforces handle."""
    query = urllib.parse.urlencode({"handle": handle, "from": 1, "count": 10000})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": "data-structure-practice-heatmap/1.0"},
    )

    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get("status") != "OK":
                raise RuntimeError(payload.get("comment", "Unknown Codeforces API error"))
            return payload["result"]
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt == attempts:
                raise RuntimeError(f"Unable to read the Codeforces API: {error}") from error
            time.sleep(2 ** (attempt - 1))

    raise RuntimeError("Unable to read the Codeforces API")


def problem_key(problem: dict) -> tuple[str, str]:
    """Build a stable identity for a regular or problemset Codeforces problem."""
    contest = problem.get("contestId") or problem.get("problemsetName") or "unknown"
    index = problem.get("index") or problem.get("name") or "unknown"
    return str(contest), str(index)


def solved_problem_dates(submissions: list[dict], timezone_name: str) -> list[date]:
    """Return the date of the first accepted submission for every unique problem."""
    timezone = ZoneInfo(timezone_name)
    solved: set[tuple[str, str]] = set()
    dates: list[date] = []

    for submission in sorted(submissions, key=lambda item: item["creationTimeSeconds"]):
        if submission.get("verdict") != "OK":
            continue
        key = problem_key(submission.get("problem", {}))
        if key in solved:
            continue
        solved.add(key)
        solved_at = datetime.fromtimestamp(submission["creationTimeSeconds"], timezone)
        dates.append(solved_at.date())

    return dates


def contribution_level(count: int, largest_count: int) -> int:
    if count == 0:
        return 0
    return min(4, max(1, math.ceil((count / largest_count) * 4)))


def render_svg(handle: str, solved_dates: list[date], today: date, timezone_name: str) -> str:
    counts = Counter(solved_dates)
    year_start = today - timedelta(days=364)
    days_since_sunday = (today.weekday() + 1) % 7
    current_week = today - timedelta(days=days_since_sunday)
    start = current_week - timedelta(weeks=52)
    grid_days = 53 * 7
    recent_solved = sum(count for day, count in counts.items() if year_start <= day <= today)
    recent_active_days = sum(1 for day, count in counts.items() if year_start <= day <= today and count)
    recent_max = max((count for day, count in counts.items() if year_start <= day <= today), default=1)

    cell = 10
    gap = 3
    pitch = cell + gap
    grid_x = 50
    grid_y = 66
    width = 790
    height = 176
    colors = ["#161b22", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        f'  <title id="title">{escape(handle)} Codeforces activity heatmap</title>',
        f'  <desc id="description">{recent_solved} problems solved across {recent_active_days} active days in the last 12 months; {len(solved_dates)} solved all time.</desc>',
        "  <style>",
        "    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #8b949e; }",
        "    .heading { fill: #f0f6fc; font-size: 13px; font-weight: 600; }",
        "    .summary { font-size: 11px; }",
        "    .label { font-size: 9px; }",
        "    .panel { fill: #0d1117; stroke: #30363d; }",
        "    .cell { stroke: #30363d; stroke-width: 0.6px; stroke-opacity: 0.75; }",
        "    .padding { fill: transparent; stroke: none; }",
        "    .cell-count { fill: #ffffff; font-size: 7px; font-weight: 700; pointer-events: none; }",
        "  </style>",
        f'  <rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" />',
        '  <text class="heading" x="18" y="22">Codeforces solving activity</text>',
        f'  <text class="summary" x="18" y="41">{recent_solved} solved · {recent_active_days} active days · last 12 months</text>',
        f'  <text class="summary" x="{width - 18}" y="22" text-anchor="end">@{escape(handle)}</text>',
    ]

    month_labels: list[tuple[int, str]] = []
    for week in range(53):
        week_start = start + timedelta(weeks=week)
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            if day.day == 1 and year_start <= day <= today:
                month_labels.append((week, day.strftime("%b")))
                break
    for week, label in month_labels:
        lines.append(f'  <text class="label" x="{grid_x + week * pitch}" y="58">{label}</text>')

    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        lines.append(f'  <text class="label" x="18" y="{grid_y + weekday * pitch + 8}">{label}</text>')

    for offset in range(grid_days):
        day = start + timedelta(days=offset)
        week = offset // 7
        weekday = offset % 7
        x = grid_x + week * pitch
        y = grid_y + weekday * pitch
        in_range = year_start <= day <= today
        count = counts[day] if in_range else 0
        level = contribution_level(count, recent_max)
        noun = "problem" if count == 1 else "problems"
        label = f"{count} {noun} solved on {day.strftime('%b')} {day.day}, {day.year}"
        cell_class = "cell" if in_range else "padding"
        lines.append(
            f'  <rect class="{cell_class}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{colors[level]}">'
        )
        lines.append(f"    <title>{escape(label)}</title>")
        lines.append("  </rect>")
        if count:
            lines.append(
                f'  <text class="cell-count" x="{x + cell / 2:g}" y="{y + 7.5:g}" text-anchor="middle">{count}</text>'
            )

    legend_y = 159
    lines.append(f'  <text class="label" x="{grid_x}" y="{legend_y + 8}">{len(solved_dates)} solved all time · first accepted solve · {escape(timezone_name)}</text>')
    legend_x = 677
    lines.append(f'  <text class="label" x="{legend_x - 26}" y="{legend_y + 8}">Less</text>')
    for level, color in enumerate(colors):
        lines.append(
            f'  <rect class="cell" x="{legend_x + level * pitch}" y="{legend_y}" width="{cell}" height="{cell}" rx="2" fill="{color}" />'
        )
    lines.append(f'  <text class="label" x="{legend_x + 5 * pitch + 2}" y="{legend_y + 8}">More</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handle", default=DEFAULT_HANDLE)
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--today", type=date.fromisoformat, help="Override today's date for testing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    today = args.today or datetime.now(ZoneInfo(args.timezone)).date()
    submissions = fetch_submissions(args.handle)
    dates = solved_problem_dates(submissions, args.timezone)
    svg = render_svg(args.handle, dates, today, args.timezone)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Generated {args.output} from {len(submissions)} submissions and {len(dates)} solved problems.")


if __name__ == "__main__":
    main()
