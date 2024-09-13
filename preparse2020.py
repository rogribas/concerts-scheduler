from bs4 import BeautifulSoup

import requests

req_24 = "https://www.barcelona.cat/lamerce/ca/cerca-esdeveniments?distr=All&venue=All&topic=3493&keytext=&sday=2020-09-24&day[min]=2020-09-24%2000:00:00&day[max]=2020-09-24%2023:59:59"
req_26 = "https://www.barcelona.cat/lamerce/ca/cerca-esdeveniments?distr=All&venue=All&topic=3493&keytext=&sday=2020-09-26&day[min]=2020-09-26%2000:00:00&day[max]=2020-09-26%2023:59:59"
req_27 = "https://www.barcelona.cat/lamerce/ca/cerca-esdeveniments?distr=All&venue=All&topic=3493&keytext=&sday=2020-09-27&day[min]=2020-09-27%2000:00:00&day[max]=2020-09-27%2023:59:59"

def parse_items(items):
    items_out = {}
    for i in items:
        title = i.find('a', attrs={'class': 'event-title'}).find('h3').text
        href = i.find('a', attrs={'class': 'event-title'})['href']
        hora = i.find('span', attrs={'class': 'hora'}).text
        lloc = i.find('div', attrs={'class': 'description'}).text.strip()

        if 'Fòrum' in lloc:
            if 'BAM' in title:
                lloc = lloc + ' 1'
            else:
                lloc = lloc + ' 2'
        
        items_out[lloc] = items_out.get(lloc, []) + [{
            'title': title,
            'href': href,
            'hora': hora
        }]
    
    return items_out

def parse_day(req):
    response = requests.get(req)
    content_search = BeautifulSoup(response.text, 'lxml')
    items = content_search.find_all('div', attrs={'class': 'back'})
    return parse_items(items)

items = {
    'Dijous 24': parse_day(req_24),
    'Dissabte 26': parse_day(req_26),
    'Diumenge 27': parse_day(req_27)
}


def print_yaml(dia, items):
    print('- %s:' % dia)
    for escenari in sorted(list(items)):
        print('    - "%s":' % escenari)
        concerts = sorted(items[escenari], key=lambda k: k['hora'])
        for c in concerts:
            # print(c['title'])
            try:
                title = c['title'].replace('Concert "','').split('"')[0]
                # print(title)
                if 'Concert' in title and not 'bandes sonores' in title:
                    # print(title)
                    title = c['title'].replace('Concert "','').split('"')[1]
                group = c['title'].replace('Concert "','').split('"')[-2]
            except:
                title = c['title']
                group = 'La Mercè és Música'
            # if 'Concert' in c['title']:
            #     break
            print("        - event: \"%s\"" % title)
            print("          time: '%s'" % c['hora'].replace(' h', ''))
            print("          link: '%s'" % c['href'])
            print("          group: '%s'" % group)


print_yaml('Dijous 24', parse_day(req_24))
print_yaml('Dissabte 26', parse_day(req_26))
print_yaml('Diumenge 27', parse_day(req_27))