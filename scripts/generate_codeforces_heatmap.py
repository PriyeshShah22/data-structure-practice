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


def longest_streak(active_days: set[date]) -> int:
    longest = 0
    current = 0
    previous: date | None = None
    for day in sorted(active_days):
        current = current + 1 if previous and day == previous + timedelta(days=1) else 1
        longest = max(longest, current)
        previous = day
    return longest


def contribution_level(count: int, largest_count: int) -> int:
    if count == 0:
        return 0
    return min(4, max(1, math.ceil((count / largest_count) * 4)))


def render_svg(handle: str, solved_dates: list[date], today: date, timezone_name: str) -> str:
    counts = Counter(solved_dates)
    days_since_sunday = (today.weekday() + 1) % 7
    current_week = today - timedelta(days=days_since_sunday)
    start = current_week - timedelta(weeks=52)
    grid_days = 53 * 7
    end = start + timedelta(days=grid_days - 1)
    visible_solved = sum(count for day, count in counts.items() if start <= day <= today)
    active_days = {day for day, count in counts.items() if count > 0}
    visible_max = max((counts[start + timedelta(days=i)] for i in range(grid_days)), default=1)
    visible_max = max(visible_max, 1)

    cell = 11
    gap = 3
    pitch = cell + gap
    grid_x = 48
    grid_y = 62
    width = 850
    height = 205
    colors = ["var(--level-0)", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="205" viewBox="0 0 850 205" role="img" aria-labelledby="title description">',
        f'  <title id="title">{escape(handle)} Codeforces activity heatmap</title>',
        f'  <desc id="description">{len(solved_dates)} problems solved all time and {visible_solved} during the displayed year.</desc>',
        "  <style>",
        "    :root { --text: #57606a; --heading: #24292f; --level-0: #ebedf0; --border: rgba(27, 31, 36, 0.06); }",
        "    @media (prefers-color-scheme: dark) { :root { --text: #8b949e; --heading: #f0f6fc; --level-0: #161b22; --border: rgba(240, 246, 252, 0.08); } }",
        "    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: var(--text); }",
        "    .heading { fill: var(--heading); font-size: 16px; font-weight: 600; }",
        "    .summary { font-size: 12px; }",
        "    .label { font-size: 10px; }",
        "    rect { stroke: var(--border); stroke-width: 1px; shape-rendering: geometricPrecision; }",
        "  </style>",
        f'  <text class="heading" x="12" y="19">{escape(handle)} · Codeforces activity</text>',
        (
            f'  <text class="summary" x="12" y="39">{len(solved_dates)} problems solved all time · '
            f'{visible_solved} in the last year · {longest_streak(active_days)} day max streak</text>'
        ),
    ]

    month_labels: list[tuple[int, str]] = [(0, start.strftime("%b"))]
    for week in range(53):
        week_start = start + timedelta(weeks=week)
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            if day.day == 1 and day != start:
                month_labels.append((week, day.strftime("%b")))
                break
    for week, label in month_labels:
        lines.append(f'  <text class="label" x="{grid_x + week * pitch}" y="55">{label}</text>')

    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        lines.append(f'  <text class="label" x="12" y="{grid_y + weekday * pitch + 9}">{label}</text>')

    for offset in range(grid_days):
        day = start + timedelta(days=offset)
        week = offset // 7
        weekday = offset % 7
        count = counts[day] if day <= today else 0
        level = contribution_level(count, visible_max)
        x = grid_x + week * pitch
        y = grid_y + weekday * pitch
        noun = "problem" if count == 1 else "problems"
        label = f"{count} {noun} solved on {day.strftime('%b')} {day.day}, {day.year}"
        lines.extend(
            [
                f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{colors[level]}">',
                f"    <title>{escape(label)}</title>",
                "  </rect>",
            ]
        )

    legend_y = 180
    lines.append(f'  <text class="label" x="{grid_x}" y="{legend_y + 9}">First accepted solve per problem · {escape(timezone_name)}</text>')
    legend_x = 714
    lines.append(f'  <text class="label" x="{legend_x - 28}" y="{legend_y + 9}">Less</text>')
    for level, color in enumerate(colors):
        lines.append(
            f'  <rect x="{legend_x + level * pitch}" y="{legend_y}" width="{cell}" height="{cell}" rx="2" fill="{color}" />'
        )
    lines.append(f'  <text class="label" x="{legend_x + 5 * pitch + 2}" y="{legend_y + 9}">More</text>')
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
