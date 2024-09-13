import requests
from bs4 import BeautifulSoup
import yaml
import re

def clean_event_name(event):
    # Remove "Concert" and quotation marks
    event = re.sub(r'^Concert\s*"|"$', '', event).strip()
    
    # Extract the main name and any additional info in parentheses
    match = re.match(r'(.+?)\s*(?:\((.+?)\))?\s*(?:a\s*[\'"](.+?)[\'"])?$', event)
    
    if match:
        name, extra_info, stage = match.groups()
        if stage:
            return f"{name.strip()} ({stage})"
        elif extra_info:
            return f"{name.strip()} ({extra_info})"
        else:
            return name.strip()
    else:
        return event

def scrape_concerts(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    concerts = {}
    
    for day_block in soup.find_all('div', class_='block-day'):
        date = day_block.get('day').split('-')[-1]
        date_str = {
            20: "DV. 20",
            21: "DS. 22",
            22: "DG. 23",
            23: "DL. 24",
            24: "DM. 25",
        }[int(date)]
        concerts[date_str] = {}
        
        for program in day_block.find_all('div', class_='wrapper-info-program'):
            location = program.find('div', class_='place').text.strip()
            if location not in concerts[date_str]:
                concerts[date_str][location] = []
            
            event = clean_event_name(program.find('h5').text.strip())
            time = program.find('div', class_='wrapper-hour-program').contents[0].strip().split(' a ')[0][:-2].replace('.', ':')
            link = 'https://www.barcelona.cat' + program.find('a')['href']
            group = program.find('span', class_='subcat-program').text.strip()
            
            concerts[date_str][location].append({
                'event': event,
                'time': time,
                'link': link,
                'group': group
            })
    
    return concerts

def generate_yaml(concerts):
    yaml_data = []
    for date, locations in concerts.items():
        date_data = {date: []}
        for location, events in locations.items():
            location_data = {location: events}
            date_data[date].append(location_data)
        yaml_data.append(date_data)
    
    return yaml.dump(yaml_data, allow_unicode=True, sort_keys=False)

url = 'https://www.barcelona.cat/lamerce/ca/programa'
concerts = scrape_concerts(url)
yaml_output = generate_yaml(concerts)

with open('schedule.yaml', 'w', encoding='utf-8') as f:
    f.write(yaml_output)

print("YAML file has been generated successfully.")