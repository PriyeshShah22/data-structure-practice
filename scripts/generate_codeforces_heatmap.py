#!/usr/bin/env python3
"""Generate a live Codeforces practice dashboard as a repository-native SVG."""

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
        headers={"User-Agent": "data-structure-practice-dashboard/2.0"},
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
    contest = problem.get("contestId") or problem.get("problemsetName") or "unknown"
    index = problem.get("index") or problem.get("name") or "unknown"
    return str(contest), str(index)


def solved_records(submissions: list[dict], timezone_name: str) -> list[dict]:
    """Return each uniquely solved problem at the time of its first accepted run."""
    timezone = ZoneInfo(timezone_name)
    solved: set[tuple[str, str]] = set()
    records: list[dict] = []
    for submission in sorted(submissions, key=lambda item: item["creationTimeSeconds"]):
        if submission.get("verdict") != "OK":
            continue
        problem = submission.get("problem", {})
        key = problem_key(problem)
        if key in solved:
            continue
        solved.add(key)
        solved_at = datetime.fromtimestamp(submission["creationTimeSeconds"], timezone)
        records.append({"date": solved_at.date(), "problem": problem})
    return records


def streaks(active_dates: set[date], today: date) -> tuple[int, int]:
    """Return the best streak and the streak ending on the latest active day."""
    if not active_dates:
        return 0, 0
    ordered = sorted(day for day in active_dates if day <= today)
    if not ordered:
        return 0, 0
    best = run = 1
    for previous, current in zip(ordered, ordered[1:]):
        run = run + 1 if current == previous + timedelta(days=1) else 1
        best = max(best, run)
    latest_day = ordered[-1]
    latest = 1
    while latest_day - timedelta(days=latest) in active_dates:
        latest += 1
    return best, latest


def contribution_level(count: int, largest_count: int) -> int:
    if count == 0:
        return 0
    return min(4, max(1, math.ceil((count / largest_count) * 4)))


def short(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def render_svg(handle: str, records: list[dict], today: date, timezone_name: str) -> str:
    solved_dates = [record["date"] for record in records]
    counts = Counter(solved_dates)
    active_dates = set(solved_dates)
    year_start = today - timedelta(days=364)
    recent_records = [record for record in records if year_start <= record["date"] <= today]
    recent_active = {record["date"] for record in recent_records}
    best_streak, latest_streak = streaks(active_dates, today)
    last_30 = sum(1 for record in records if today - timedelta(days=29) <= record["date"] <= today)

    ratings = Counter(record["problem"].get("rating", "Unrated") for record in records)
    tags = Counter(tag for record in records for tag in record["problem"].get("tags", []))
    rating_rows = sorted(ratings.items(), key=lambda item: (item[0] == "Unrated", str(item[0])))[:4]
    tag_rows = tags.most_common(4)
    recent_wins = sorted(records, key=lambda record: record["date"], reverse=True)[:3]

    days_since_sunday = (today.weekday() + 1) % 7
    current_week = today - timedelta(days=days_since_sunday)
    start = current_week - timedelta(weeks=52)
    recent_max = max((counts[day] for day in recent_active), default=1)

    width, height = 1000, 640
    grid_x, grid_y = 108, 306
    cell, pitch = 10, 14
    colors = ["#151d2c", "#164e63", "#0e7490", "#06b6d4", "#67e8f9"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        f'  <title id="title">@{escape(handle)} Codeforces Practice Pulse</title>',
        f'  <desc id="description">A live practice dashboard showing {len(records)} unique solved problems, {len(active_dates)} active days, and a {best_streak}-day best streak.</desc>',
        "  <defs>",
        '    <linearGradient id="canvas" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#08111f"/><stop offset="1" stop-color="#0d0b1c"/></linearGradient>',
        '    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#22d3ee"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>',
        '    <linearGradient id="soft" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#22d3ee" stop-opacity=".12"/><stop offset="1" stop-color="#a78bfa" stop-opacity=".08"/></linearGradient>',
        '    <filter id="glow"><feGaussianBlur stdDeviation="18"/></filter>',
        "  </defs>",
        "  <style>",
        "    text { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #94a3b8; }",
        "    .title { fill: #f8fafc; font-size: 25px; font-weight: 750; letter-spacing: -.4px; }",
        "    .eyebrow { fill: #67e8f9; font-size: 10px; font-weight: 700; letter-spacing: 1.8px; }",
        "    .subtitle { font-size: 12px; } .label { font-size: 10px; } .tiny { font-size: 9px; }",
        "    .value { fill: #f8fafc; font-size: 25px; font-weight: 750; }",
        "    .section { fill: #e2e8f0; font-size: 13px; font-weight: 650; }",
        "    .strong { fill: #e2e8f0; font-size: 11px; font-weight: 600; }",
        "    .panel { fill: #0c1422; stroke: #263247; stroke-width: 1; }",
        "    .card { fill: url(#soft); stroke: #263247; stroke-width: 1; }",
        "    .cell { stroke: #334155; stroke-width: .7; } .padding { fill: transparent; stroke: none; }",
        "    .cell-count { fill: #f8fafc; font-size: 7px; font-weight: 750; pointer-events: none; }",
        "  </style>",
        f'  <rect width="{width}" height="{height}" rx="18" fill="url(#canvas)"/>',
        '  <circle cx="850" cy="35" r="115" fill="#7c3aed" opacity=".10" filter="url(#glow)"/>',
        '  <rect x="1" y="1" width="998" height="638" rx="17" fill="none" stroke="#263247"/>',
        '  <rect x="36" y="28" width="4" height="52" rx="2" fill="url(#accent)"/>',
        '  <text class="eyebrow" x="56" y="39">CODEFORCES · LEARNING IN PUBLIC</text>',
        '  <text class="title" x="56" y="68">Practice Pulse</text>',
        f'  <text class="subtitle" x="964" y="43" text-anchor="end">@{escape(handle)}</text>',
        f'  <text class="label" x="964" y="65" text-anchor="end">CP-31 journey · updated {today.strftime("%d %b %Y")}</text>',
    ]

    stats = [
        ("UNIQUE SOLVES", str(len(records)), "first accepted problems"),
        ("ACTIVE DAYS", str(len(active_dates)), "across all recorded time"),
        ("BEST STREAK", f"{best_streak}d", f"latest run: {latest_streak} day" + ("s" if latest_streak != 1 else "")),
        ("LAST 30 DAYS", str(last_30), "new problems cleared"),
    ]
    for index, (label, value, detail) in enumerate(stats):
        x = 36 + index * 232
        lines.extend([
            f'  <rect class="card" x="{x}" y="101" width="212" height="91" rx="12"/>',
            f'  <text class="eyebrow" x="{x + 18}" y="124">{label}</text>',
            f'  <text class="value" x="{x + 18}" y="157">{value}</text>',
            f'  <text class="tiny" x="{x + 18}" y="177">{escape(detail)}</text>',
        ])

    lines.extend([
        '  <rect class="panel" x="36" y="216" width="928" height="224" rx="14"/>',
        '  <text class="section" x="56" y="246">365-day solving trail</text>',
        f'  <text class="label" x="944" y="246" text-anchor="end">{len(recent_records)} solves · {len(recent_active)} active days</text>',
    ])

    month_labels: list[tuple[int, str]] = []
    for week in range(53):
        week_start = start + timedelta(weeks=week)
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            if day.day == 1 and year_start <= day <= today:
                month_labels.append((week, day.strftime("%b")))
                break
    for week, label in month_labels:
        lines.append(f'  <text class="label" x="{grid_x + week * pitch}" y="286">{label}</text>')
    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        lines.append(f'  <text class="label" x="60" y="{grid_y + weekday * pitch + 8}">{label}</text>')

    for offset in range(53 * 7):
        day = start + timedelta(days=offset)
        week, weekday = divmod(offset, 7)
        x, y = grid_x + week * pitch, grid_y + weekday * pitch
        in_range = year_start <= day <= today
        count = counts[day] if in_range else 0
        level = contribution_level(count, recent_max)
        noun = "problem" if count == 1 else "problems"
        cell_class = "cell" if in_range else "padding"
        lines.append(f'  <rect class="{cell_class}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{colors[level]}"><title>{count} {noun} solved on {day.strftime("%d %b %Y")}</title></rect>')
        if count:
            lines.append(f'  <text class="cell-count" x="{x + 5}" y="{y + 7.5}" text-anchor="middle">{count}</text>')

    lines.append(f'  <text class="tiny" x="60" y="420">Each square marks a first accepted solution · {escape(timezone_name)}</text>')
    legend_x = 848
    lines.append(f'  <text class="tiny" x="{legend_x - 34}" y="420">LESS</text>')
    for level, color in enumerate(colors):
        lines.append(f'  <rect class="cell" x="{legend_x + level * 15}" y="410" width="10" height="10" rx="2.5" fill="{color}"/>')
    lines.append(f'  <text class="tiny" x="{legend_x + 80}" y="420">MORE</text>')

    panels = [(36, 300, "DIFFICULTY LADDER"), (354, 300, "TOPIC FINGERPRINT"), (672, 292, "RECENT WINS")]
    for x, panel_width, heading in panels:
        lines.extend([
            f'  <rect class="panel" x="{x}" y="460" width="{panel_width}" height="147" rx="14"/>',
            f'  <text class="eyebrow" x="{x + 18}" y="486">{heading}</text>',
        ])

    rating_max = max((count for _, count in rating_rows), default=1)
    for index, (rating, count) in enumerate(rating_rows):
        y = 510 + index * 22
        bar_width = 172 * count / rating_max
        lines.extend([
            f'  <text class="label" x="54" y="{y + 8}">{escape(str(rating))}</text>',
            f'  <rect x="103" y="{y}" width="172" height="9" rx="4.5" fill="#172033"/>',
            f'  <rect x="103" y="{y}" width="{bar_width:.1f}" height="9" rx="4.5" fill="url(#accent)"/>',
            f'  <text class="tiny" x="314" y="{y + 8}" text-anchor="end">{count}</text>',
        ])

    tag_max = max((count for _, count in tag_rows), default=1)
    for index, (tag, count) in enumerate(tag_rows):
        y = 510 + index * 22
        bar_width = 122 * count / tag_max
        lines.extend([
            f'  <text class="label" x="372" y="{y + 8}">{escape(short(tag, 16))}</text>',
            f'  <rect x="492" y="{y}" width="122" height="9" rx="4.5" fill="#172033"/>',
            f'  <rect x="492" y="{y}" width="{bar_width:.1f}" height="9" rx="4.5" fill="#a78bfa"/>',
            f'  <text class="tiny" x="632" y="{y + 8}" text-anchor="end">{count}</text>',
        ])

    for index, record in enumerate(recent_wins):
        problem = record["problem"]
        contest = problem.get("contestId", "")
        problem_id = f'{contest}{problem.get("index", "")}'
        y = 513 + index * 34
        lines.extend([
            f'  <circle cx="692" cy="{y}" r="4" fill="#22d3ee"/>',
            f'  <text class="strong" x="705" y="{y + 3}">{escape(short(problem.get("name", "Unknown problem"), 27))}</text>',
            f'  <text class="tiny" x="944" y="{y + 3}" text-anchor="end">{escape(problem_id)} · {record["date"].strftime("%d %b")}</text>',
        ])

    lines.extend([
        '  <rect x="36" y="623" width="928" height="1" fill="#263247"/>',
        '  <text class="tiny" x="36" y="636">LIVE FROM THE CODEFORCES API · UNIQUE FIRST ACCEPTED SOLVES</text>',
        '  <text class="tiny" x="964" y="636" text-anchor="end">KEEP SHOWING UP ↗</text>',
        "</svg>",
    ])
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
    records = solved_records(submissions, args.timezone)
    svg = render_svg(args.handle, records, today, args.timezone)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Generated {args.output} from {len(submissions)} submissions and {len(records)} solved problems.")


if __name__ == "__main__":
    main()
