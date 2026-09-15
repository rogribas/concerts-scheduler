# -*- coding: utf-8 -*-
"""
Generate a single, dependency-free static HTML page that shows the Mercè
music schedule as a Clashfinder-style grid: venues as columns, time of day
as the vertical axis, one tab per day. No JavaScript is used — the day
switcher is a pure CSS radio/label trick, so the page works everywhere.

Input:  schedule.yaml   (list of {date, period, locations: [{name: [events]}]})
Output: docs/index.html
"""

import os
import html
from collections import OrderedDict, defaultdict
from datetime import datetime

import yaml

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
SCHEDULE_FILE = "schedule.yaml"
OUTPUT_DIR = "docs"
OUTPUT_FILE = "index.html"

PX_PER_MIN = 2.1          # vertical scale of the grid (bigger = taller/roomier)
DAY_START_HOUR = 10       # clock hours below this are treated as "after midnight"
STAGE_COL_WIDTH = 220     # px, width of each venue column
TIME_COL_WIDTH = 60       # px, width of the sticky time gutter
HEADER_HEIGHT = 60        # px, sticky header row height
MIN_EVENT_HEIGHT = 30     # px, minimum block height so short sets stay readable

# A curated palette of medium-dark, saturated colours: white text reads well
# on all of them, and each distinct "group" (musical genre) gets a stable
# colour because it's picked deterministically from a hash of its text.
PALETTE = [
    "#c1121f", "#284b63", "#2a9d8f", "#6a4c93", "#bb3e03",
    "#3d5a80", "#7209b7", "#08605f", "#9d4edd", "#5f0f40",
    "#264653", "#8d0801", "#3a5a40", "#495867", "#941b0c",
    "#006d77", "#7b2cbf", "#9a031e",
]


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_days(path):
    """Load schedule.yaml and merge entries that share the same date
    (the scraper emits one entry per date+period, e.g. 24-setembre/Mati,
    24-setembre/Tarda, 24-setembre/Nit all describe the same calendar day).
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []

    days = OrderedDict()
    for entry in raw:
        date = (entry.get("date") or "").strip()
        if not date:
            continue
        bucket = days.setdefault(date, defaultdict(list))
        for loc_block in entry.get("locations", []) or []:
            for location, events in loc_block.items():
                bucket[location].extend(events or [])

    # The site repeats the boundary event across adjacent periods (e.g. an
    # event still playing at the Mati/Tarda cutoff shows up in both lists).
    # De-duplicate identical (event, start, end) entries per venue.
    for date, locations in days.items():
        for location, events in list(locations.items()):
            seen = set()
            unique = []
            for ev in events:
                key = (ev.get("event"), ev.get("start_time"), ev.get("end_time"))
                if key in seen:
                    continue
                seen.add(key)
                unique.append(ev)
            unique.sort(key=lambda e: to_minutes(e["start_time"]))
            locations[location] = unique

    return days


# --------------------------------------------------------------------------
# Time helpers
# --------------------------------------------------------------------------
def to_minutes(time_str):
    h, m = map(int, time_str.split(":"))
    total = h * 60 + m
    if h < DAY_START_HOUR:
        total += 24 * 60  # past midnight -> continues the same timeline
    return total


def event_span(event):
    start = to_minutes(event["start_time"])
    end = to_minutes(event["end_time"])
    if end <= start:
        end += 24 * 60
    return start, end


def color_for(text):
    if not text:
        return PALETTE[0]
    return PALETTE[sum(ord(c) for c in text) % len(PALETTE)]


def esc(value):
    return html.escape(str(value), quote=True)


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------
def render_day_view(index, date, locations):
    all_events = [ev for evs in locations.values() for ev in evs]
    if not all_events:
        day_min, day_max = DAY_START_HOUR * 60, (DAY_START_HOUR + 10) * 60
    else:
        starts = [to_minutes(ev["start_time"]) for ev in all_events]
        ends = [event_span(ev)[1] for ev in all_events]
        day_min = (min(starts) // 60) * 60
        day_max = -(-max(ends) // 60) * 60  # round up to the next full hour

    total_minutes = day_max - day_min
    total_height = round(total_minutes * PX_PER_MIN)
    hour_height = round(60 * PX_PER_MIN)

    # Sticky time gutter, one label per hour
    marks = []
    minute = day_min
    while minute <= day_max:
        top = round((minute - day_min) * PX_PER_MIN)
        label_hour = (minute // 60) % 24
        marks.append(f'<span class="time-mark" style="top:{top}px">{label_hour:02d}:00</span>')
        minute += 60
    time_marks_html = "".join(marks)

    # One column per venue, alphabetically ordered so a venue sits in a
    # stable position from day to day.
    stage_cols = []
    for location in sorted(locations.keys(), key=str.casefold):
        blocks = []
        for ev in locations[location]:
            start, end = event_span(ev)
            top = round((start - day_min) * PX_PER_MIN)
            height = max(round((end - start) * PX_PER_MIN), MIN_EVENT_HEIGHT)
            time_label = f'{ev.get("start_time", "")}\u2013{ev.get("end_time", "")}'
            tooltip = f'{ev.get("event", "")} \u00b7 {time_label} \u00b7 {location}'

            # Very short sets don't have room for time + name + genre: drop
            # the least essential lines first so text never overlaps.
            inner = f'<span class="event-name">{esc(ev.get("event", ""))}</span>'
            if height >= 40:
                inner = f'<span class="event-time">{esc(time_label)}</span>' + inner
            if height >= 58:
                inner += f'<span class="event-group">{esc(ev.get("group", ""))}</span>'

            blocks.append(
                '<a class="event" style="top:{top}px;height:{height}px;background:{color}" '
                'href="{link}" target="_blank" rel="noopener" title="{tooltip}">{inner}</a>'.format(
                    top=top,
                    height=height,
                    color=color_for(ev.get("group", "")),
                    link=esc(ev.get("link") or "#"),
                    tooltip=esc(tooltip),
                    inner=inner,
                )
            )
        stage_cols.append(
            '<div class="stage-col">'
            '<div class="stage-header">{location}</div>'
            '<div class="stage-body" style="height:{h}px">{blocks}</div>'
            "</div>".format(location=esc(location), h=total_height, blocks="".join(blocks))
        )

    return (
        '<div class="day-view" id="view-{i}">'
        '<div class="grid-scroll">'
        '<div class="grid">'
        '<div class="time-col">'
        '<div class="corner"></div>'
        '<div class="time-marks" style="height:{h}px">{marks}</div>'
        "</div>"
        '<div class="stages">{stages}</div>'
        "</div></div></div>"
    ).format(i=index, h=total_height, marks=time_marks_html, stages="".join(stage_cols))


def render_tabs_and_rules(dates):
    radios, labels, rules = [], [], []
    for i, date in enumerate(dates):
        checked = " checked" if i == 0 else ""
        radios.append(f'<input type="radio" name="day" id="day-{i}" class="day-radio"{checked}>')
        labels.append(f'<label for="day-{i}">{esc(date)}</label>')
        rules.append(
            f'#day-{i}:checked ~ .day-tabs label[for="day-{i}"]{{background:var(--accent);'
            f"color:#fff;border-color:var(--accent);box-shadow:0 2px 10px rgba(0,0,0,.25)}}\n"
            f'#day-{i}:checked ~ .day-views #view-{i}{{display:block}}\n'
            f'#day-{i}:focus-visible ~ .day-tabs label[for="day-{i}"]{{outline:2px solid var(--accent);'
            f"outline-offset:2px}}"
        )
    return "".join(radios), "".join(labels), "\n".join(rules)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Programa de música — La Mercè</title>
<style>
:root {{
  --bg: #0f1116;
  --panel: #171a21;
  --panel-2: #1e222b;
  --text: #eef0f5;
  --muted: #9aa2b1;
  --border: #2a2f3a;
  --accent: #ef476f;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
.page-header {{ text-align: center; padding: 36px 20px 6px; }}
.page-header h1 {{ margin: 0 0 6px; font-size: 28px; letter-spacing: .3px; }}
.page-header p {{ margin: 0; color: var(--muted); font-size: 14px; }}

.day-tabs {{
  display: flex; flex-wrap: wrap; justify-content: center; gap: 8px;
  padding: 22px 16px 24px;
}}
.day-tabs label {{
  padding: 10px 18px; border-radius: 999px; cursor: pointer; user-select: none;
  background: var(--panel); color: var(--muted); border: 1px solid var(--border);
  font-weight: 600; font-size: 14px; transition: background .15s ease, color .15s ease;
}}
.day-tabs label:hover {{ color: var(--text); border-color: var(--accent); }}
.day-radio {{ position: absolute; opacity: 0; width: 1px; height: 1px; overflow: hidden; }}

.day-view {{ display: none; padding: 0 16px 48px; text-align: center; }}

.grid-scroll {{
  display: inline-block; text-align: left; width: fit-content;
  max-width: 100%; overflow: auto; max-height: 74vh;
  border: 1px solid var(--border); border-radius: 14px; background: var(--panel);
}}
.grid {{ display: flex; width: max-content; }}

.time-col {{
  position: sticky; left: 0; z-index: 3; width: {time_col_width}px; flex-shrink: 0;
  background: var(--panel); border-right: 1px solid var(--border);
}}
.corner {{
  position: sticky; top: 0; z-index: 4; height: {header_height}px;
  background: var(--panel); border-bottom: 1px solid var(--border);
}}
.time-marks {{ position: relative; }}
.time-mark {{
  position: absolute; left: 0; right: 6px; transform: translateY(-50%);
  font-size: 11px; color: var(--muted); text-align: right;
}}

.stages {{ display: flex; }}
.stage-col {{ width: {stage_col_width}px; flex-shrink: 0; border-right: 1px solid var(--border); }}
.stage-header {{
  position: sticky; top: 0; z-index: 2; height: {header_height}px;
  background: var(--panel-2); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center; text-align: center;
  font-weight: 700; font-size: 12.5px; line-height: 1.25; padding: 6px 10px;
}}
.stage-body {{
  position: relative;
  background-image: repeating-linear-gradient(
    to bottom, var(--border) 0, var(--border) 1px,
    transparent 1px, transparent {hour_height}px
  );
}}

.event {{
  position: absolute; left: 4px; right: 4px; border-radius: 8px;
  padding: 6px 8px; overflow: hidden; text-decoration: none; color: #fff;
  display: flex; flex-direction: column; gap: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,.35);
  transition: transform .12s ease, box-shadow .12s ease;
}}
.event:hover, .event:focus-visible {{
  transform: scale(1.03); box-shadow: 0 6px 16px rgba(0,0,0,.45); z-index: 5;
  outline: none;
}}
.event-time {{ font-size: 10.5px; font-weight: 700; opacity: .9; }}
.event-name {{
  font-size: 12.5px; font-weight: 700; line-height: 1.2;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  text-shadow: 0 1px 2px rgba(0,0,0,.35);
}}
.event-group {{
  font-size: 10px; font-style: italic; opacity: .85; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}}

.page-footer {{
  text-align: center; color: var(--muted); font-size: 12.5px; padding: 8px 16px 40px;
}}
.page-footer a {{ color: var(--muted); }}

@media (max-width: 640px) {{
  .page-header h1 {{ font-size: 22px; }}
  .stage-col {{ width: 180px; }}
}}
{tab_rules}
</style>
</head>
<body>
<div class="page-header">
  <h1>Programa de música — La Mercè</h1>
  <p>{n_days} dies · {n_events} concerts · tria un dia i mira'l hora a hora</p>
</div>

{radios}

<div class="day-tabs">
{labels}
</div>

<div class="day-views">
{day_views}
</div>

<div class="page-footer">
  Generat automàticament el {generated} a partir de
  <a href="https://www.barcelona.cat/lamerce/ca/musica-merce" target="_blank" rel="noopener">barcelona.cat/lamerce</a>.
</div>
</body>
</html>
"""


def build_html(days):
    dates = list(days.keys())
    radios, labels, tab_rules = render_tabs_and_rules(dates)
    day_views = "\n".join(render_day_view(i, date, days[date]) for i, date in enumerate(dates))
    n_events = sum(len(evs) for locs in days.values() for evs in locs.values())

    return PAGE_TEMPLATE.format(
        time_col_width=TIME_COL_WIDTH,
        header_height=HEADER_HEIGHT,
        stage_col_width=STAGE_COL_WIDTH,
        hour_height=round(60 * PX_PER_MIN),
        tab_rules=tab_rules,
        n_days=len(dates),
        n_events=n_events,
        radios=radios,
        labels=labels,
        day_views=day_views,
        generated=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
if __name__ == "__main__":
    days = load_days(SCHEDULE_FILE)
    if not days:
        print("Error: schedule.yaml is empty or invalid.")
        raise SystemExit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for item in os.listdir(OUTPUT_DIR):
        if item.endswith(".html"):
            os.remove(os.path.join(OUTPUT_DIR, item))

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(build_html(days))

    n_events = sum(len(evs) for locs in days.values() for evs in locs.values())
    print(f"Wrote {output_path}  ({len(days)} days, {n_events} events)")