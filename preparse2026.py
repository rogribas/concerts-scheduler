import requests
from bs4 import BeautifulSoup
import yaml
import re
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MerceScraper/1.0)"
}


def clean_event_name(text):
    """'Concert 'X'' / 'Espectacle 'X'.' -> 'X'"""
    text = text.strip().rstrip(".")

    match = re.match(
        r"""^(?:Concert|Espectacle)(?:\s+de)?\s+['"](.+?)['"]$""",
        text,
    )

    if match:
        return match.group(1).strip()

    return text


def parse_time_range(hour_text):
    """'21.00 h a 22.30 h' -> ('21:00', '22:30')"""
    parts = [p.strip() for p in hour_text.split(" a ")]

    def normalize(t):
        t = t.replace(" h", "").strip()

        # Support both 21.00 and 21:00
        if ":" in t:
            h, _, m = t.partition(":")
        else:
            h, _, m = t.partition(".")

        m = m or "00"

        return f"{int(h):02d}:{m.zfill(2)}"

    start = normalize(parts[0]) if parts else ""
    end = normalize(parts[1]) if len(parts) > 1 else ""

    return start, end


def scrape_concerts(url):
    """
    Scrape events from a Merce/BAM page.

    Returns:
        [
            {
                "date": "...",
                "period": "...",
                "locations": {
                    "Stage": [
                        {...},
                        ...
                    ]
                }
            },
            ...
        ]
    """
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    sections = []

    for section in soup.select("div.term-section"):
        header = section.find("h3")

        if not header:
            continue

        header_text = header.get_text(strip=True)
        parts = header_text.split()

        if not parts:
            continue

        # Last word is expected to be Nit / Matí / Tarda
        period = parts[-1]
        date_str = " ".join(parts[:-1])

        locations = {}

        for event_node in section.select("div.node.node--type-event"):
            raw_name = ""

            try:
                # Location / stage
                place_div = event_node.select_one("div.place")
                location = (
                    place_div.get_text(strip=True)
                    if place_div
                    else "Desconegut"
                )

                # Event name
                name_p = event_node.select_one("div.name p")
                raw_name = (
                    name_p.get_text(strip=True)
                    if name_p
                    else ""
                )

                event_name = clean_event_name(raw_name)

                # Time
                hour_span = event_node.select_one("span.hour")

                if hour_span:
                    start_time, end_time = parse_time_range(
                        hour_span.get_text(strip=True)
                    )
                else:
                    start_time, end_time = "", ""

                # Link
                a_tag = event_node.find("a", href=True)

                link = (
                    urljoin(url, a_tag["href"])
                    if a_tag
                    else ""
                )

                # Group / subcategory
                subcat_span = event_node.select_one(
                    "div.card-subcategory span"
                )

                group = (
                    subcat_span.get_text(strip=True)
                    if subcat_span
                    else ""
                )

                event = {
                    "event": event_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "link": link,
                    "group": group,
                }

                locations.setdefault(location, []).append(event)

            except Exception as e:
                print(
                    f"Error parsing event ({raw_name!r}) "
                    f"in '{header_text}': {e}"
                )

        sections.append(
            {
                "date": date_str,
                "period": period,
                "locations": locations,
            }
        )

    return sections


def merge_sections(*section_lists):
    """
    Merge sections from multiple scraped URLs.

    Sections are considered the same when they have the same:
        date + period

    Locations/stages are then merged underneath them.

    This means that if both Merce and BAM contain:

        23 de setembre / Nit / Plaça Catalunya

    their events will all appear under the same location.
    """
    merged = {}

    for sections in section_lists:
        for section in sections:
            section_key = (
                section["date"],
                section["period"],
            )

            if section_key not in merged:
                merged[section_key] = {
                    "date": section["date"],
                    "period": section["period"],
                    "locations": {},
                }

            target_section = merged[section_key]

            for location, events in section["locations"].items():
                target_section["locations"].setdefault(
                    location,
                    []
                ).extend(events)

    return list(merged.values())


def deduplicate_events(sections):
    """
    Remove duplicate events after merging.

    An event is considered identical when all of these match:
        event
        start_time
        end_time
        link
        group

    This prevents the same event appearing twice if it happens
    to be present on both source pages.
    """
    for section in sections:
        for location, events in section["locations"].items():
            seen = set()
            unique_events = []

            for event in events:
                key = (
                    event.get("event", ""),
                    event.get("start_time", ""),
                    event.get("end_time", ""),
                    event.get("link", ""),
                    event.get("group", ""),
                )

                if key not in seen:
                    seen.add(key)
                    unique_events.append(event)

            section["locations"][location] = unique_events

    return sections


def generate_yaml(sections):
    yaml_data = []

    for section in sections:
        entry = {
            "date": section["date"],
            "period": section["period"],
            "locations": [
                {loc: events}
                for loc, events in section["locations"].items()
            ],
        }

        yaml_data.append(entry)

    return yaml.dump(
        yaml_data,
        allow_unicode=True,
        sort_keys=False,
    )


if __name__ == "__main__":
    url = (
        "https://www.barcelona.cat/"
        "lamerce/ca/musica-merce?date=all"
    )

    url2 = (
        "https://www.barcelona.cat/"
        "lamerce/ca/bam-barcelona-accio-musical?date=all"
    )

    # Scrape both sources
    merce_sections = scrape_concerts(url)
    bam_sections = scrape_concerts(url2)

    # Merge by date + period, then merge stages/locations
    sections = merge_sections(
        merce_sections,
        bam_sections,
    )

    # Remove duplicates that may occur across the two sources
    sections = deduplicate_events(sections)

    # Generate YAML
    yaml_output = generate_yaml(sections)

    with open(
        "schedule.yaml",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(yaml_output)

    total_events = sum(
        len(events)
        for section in sections
        for events in section["locations"].values()
    )

    print(
        "YAML file has been generated successfully "
        f"({total_events} events, {len(sections)} time blocks)."
    )
