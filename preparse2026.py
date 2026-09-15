import requests
from bs4 import BeautifulSoup
import yaml
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MerceScraper/1.0)"}


def clean_event_name(text):
    """'Concert 'X'' / 'Espectacle 'X'.' -> 'X'"""
    text = text.strip().rstrip(".")
    match = re.match(r"^(?:Concert|Espectacle)(?:\s+de)?\s+['\"](.+?)['\"]$", text)
    if match:
        return match.group(1).strip()
    return text


def parse_time_range(hour_text):
    """'21.00 h a 22.30 h' -> ('21:00', '22:30')"""
    parts = [p.strip() for p in hour_text.split(" a ")]

    def normalize(t):
        t = t.replace(" h", "").strip()
        h, _, m = t.partition(".")
        m = m or "00"
        return f"{int(h):02d}:{m.zfill(2)}"

    start = normalize(parts[0]) if parts else ""
    end = normalize(parts[1]) if len(parts) > 1 else ""
    return start, end


def scrape_concerts(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    sections = []

    for section in soup.select("div.term-section"):
        header = section.find("h3")
        if not header:
            continue

        header_text = header.get_text(strip=True)
        parts = header_text.split()
        period = parts[-1]                # Nit / Matí / Tarda
        date_str = " ".join(parts[:-1])   # e.g. "23 de setembre"

        locations = {}

        for event_node in section.select("div.node.node--type-event"):
            raw_name = ""
            try:
                place_div = event_node.select_one("div.place")
                location = place_div.get_text(strip=True) if place_div else "Desconegut"

                name_p = event_node.select_one("div.name p")
                raw_name = name_p.get_text(strip=True) if name_p else ""
                event_name = clean_event_name(raw_name)

                hour_span = event_node.select_one("span.hour")
                start_time, end_time = (
                    parse_time_range(hour_span.get_text(strip=True)) if hour_span else ("", "")
                )

                a_tag = event_node.find("a", href=True)
                link = "https://www.barcelona.cat" + a_tag["href"] if a_tag else ""

                subcat_span = event_node.select_one("div.card-subcategory span")
                group = subcat_span.get_text(strip=True) if subcat_span else ""

                locations.setdefault(location, []).append(
                    {
                        "event": event_name,
                        "start_time": start_time,
                        "end_time": end_time,
                        "link": link,
                        "group": group,
                    }
                )
            except Exception as e:
                print(f"Error parsing event ({raw_name!r}) in '{header_text}': {e}")

        sections.append({"date": date_str, "period": period, "locations": locations})

    return sections


def generate_yaml(sections):
    yaml_data = []
    for section in sections:
        entry = {
            "date": section["date"],
            "period": section["period"],
            "locations": [{loc: events} for loc, events in section["locations"].items()],
        }
        yaml_data.append(entry)
    return yaml.dump(yaml_data, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    url = "https://www.barcelona.cat/lamerce/ca/musica-merce?date=all"
    sections = scrape_concerts(url)

    yaml_output = generate_yaml(sections)
    with open("schedule.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_output)

    total_events = sum(len(v) for s in sections for v in s["locations"].values())
    print(f"YAML file has been generated successfully ({total_events} events, {len(sections)} time blocks).")