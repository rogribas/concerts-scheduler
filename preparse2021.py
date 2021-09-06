from bs4 import BeautifulSoup

import requests

req = "https://www.barcelona.cat/lamerce/ca/cerca?topic=3307"



def parse_items(items):
    items_days = {}
    for i in items:
        name = i.find('div', attrs={'class': 'name'}).find('span').text
        href = "https://www.barcelona.cat" + i.find('a')['href']
        projection = i.find('div', attrs={'class': 'projection'}).text
        dia = projection.split(' · ')[0]
        hora = projection.split(' · ')[1].replace('H', '').strip()
        lloc = i.find('div', attrs={'class': 'place'}).text.strip()

        # if 'Fòrum' in lloc:
        #     if 'BAM' in title:
        #         lloc = lloc + ' 1'
        #     else:
        #         lloc = lloc + ' 2'

        items_days[dia] = items_days.get(dia, {})
        
        items_days[dia][lloc] = items_days[dia].get(lloc, []) + [{
            'title': name,
            'href': href,
            'hora': hora
        }]
    
    return items_days


response = requests.get(req)
content_search = BeautifulSoup(response.text, 'html.parser')
items = content_search.find_all('div', attrs={'class': 'node--type-event'})

items_days = parse_items(items)

for dia, items in items_days.items():
    print('- %s:' % dia)
    for escenari in sorted(list(items)):
        print('    - "%s":' % escenari)
        concerts = sorted(items[escenari], key=lambda k: k['hora'])
        for c in concerts:
            # print(c['title'])
            try:
                title = c['title'].replace('Concert "','').split('"')[0]
                # print(title)
                # if 'Concert' in title and not 'bandes sonores' in title:
                #     # print(title)
                #     title = c['title'].replace('Concert "','').split('"')[1]
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


