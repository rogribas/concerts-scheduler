from bs4 import BeautifulSoup

import requests

req = "https://www.barcelona.cat/lamerce/ca/cerca?topic=8361"



def parse_items(items):
    items_days = {}
    for i in items:
        name = i.find('div', attrs={'class': 'name'}).find('span').text
        # print(name)
        href = "https://www.barcelona.cat" + i.find('a')['href']
        projection = i.find('div', attrs={'class': 'projection'}).text
        dia = projection.split(' · ')[0]
        hora = projection.split(' · ')[1].replace('H', '').strip()
        if not i.find('div', attrs={'class': 'place'}):
            print(href)
            lloc = input(name)
        else:
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

with open("schedule.yaml", "a") as f:
    for dia, items in items_days.items():
        print('- %s:' % dia, file=f)
        for escenari in sorted(list(items)):
            print('    - "%s":' % escenari, file=f)
            concerts = sorted(items[escenari], key=lambda k: k['hora'])
            for c in concerts:
                # print(c['title'])
                c_title = c['title']
                try:
                    # print('pre', c['title'])
                    if 'Concert de ' in c_title:
                        title = c_title.replace('Concert de "','').split('"')[0]
                        group = c_title.replace('Concert de "','').split('"')[-2]
                    elif 'Concert  "' in c_title:
                        title = c_title.replace('Concert  "','').split('"')[0]
                        group = c_title.replace('Concert  "','').split('"')[-2]
                    else:
                        title = c_title.replace('Concert "','').split('"')[0]
                        # if 'Concert' in title and not 'bandes sonores' in title:
                        #     # print(title)
                        #     title = c['title'].replace('Concert "','').split('"')[1]
                        group = c_title.replace('Concert "','').split('"')[-2]

                    # print(title)
                except:
                    title = c['title']
                    # print(111111, title)
                    group = 'Mercè Música'
                
                if 'BAM' in group:
                    group = 'BAM'
                # if 'Concert' in c['title']:
                #     break
                print("        - event: \"%s\"" % title, file=f)
                print("          time: '%s'" % c['hora'].replace(' h', ''), file=f)
                print("          link: '%s'" % c['href'], file=f)
                print("          group: '%s'" % group, file=f)


