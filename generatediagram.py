import requests
from bs4 import BeautifulSoup
import sys

influences = {}
influenced = {}
scraped = []

def getName(link):
    if link.startswith("https://en.wikipedia.org/wiki"):
        try:
            r = requests.get(link)
        except:
            print("Error")
            raise
            return ""
        
        soup = BeautifulSoup(r.content, 'html.parser')
        if soup.find('span', class_='mw-page-title-main'):
            return soup.find('span', class_='mw-page-title-main').text
        else:
            return link.replace('https://en.wikipedia.org/wiki/','')
    else:
        print(link)
        return ""

# Generate an AdjacencyList
def scrape(link,n):
    if not link.startswith("https://en.wikipedia.org/wiki"):
        print(link)
        return
    try:
        r = requests.get(link)
    except:
        print("Error")
        raise
        return
     
    soup = BeautifulSoup(r.content, 'html.parser')
    page_name = getName(link)
    if page_name in scraped:
        #print(n*'.'+'"'+page_name+'"')
        return
    scraped.append(page_name)
    print('\t'+(n*' ')+'"'+page_name+'"')
    #infobox = soup.find('table', class_='infobox biography vcard')
    #print(soup.find('div', string='Influences').parent)
    if soup.find('div', string='Influences'):
        for child in soup.find('div', string='Influences').parent.descendants:
            if child.name == 'a':
                # child['href'] is the link to the influence
                # Add to adjacency list by webpage name and recurse if the person is new
                if child.get('href'):
                    influencer_link = 'https://en.wikipedia.org' + child['href']
                    influencer = getName(influencer_link)
                    if influencer == 'Main Page':
                        continue
                    if influencer != "":
                        influences.setdefault(page_name,[])
                        influences[page_name].append(influencer)
                        if not (influencer in influences.keys()):
                            print(">", end = '')
                            scrape(influencer_link,n+1)
                else:
                    print(child)
            
    if soup.find('div', string='Influenced'):
        for child in soup.find('div', string='Influenced').parent.descendants:
            if child.name == 'a':
                # child['href'] is the link to the influence
                # Add to adjacency list by webpage name and recurse if the person is new
                if child.get('href'):
                    influencee_link = 'https://en.wikipedia.org' + child['href']
                    influencee = getName(influencee_link)
                    if influencee == 'Main Page':
                        continue
                    if influencee != "":
                        influenced.setdefault(page_name,[])
                        influenced[page_name].append(influencee)
                        if not (influencee in influenced.keys()):
                            #print("<", end = '')
                            scrape(influencee_link,n+1)
                else:
                    print(child)
    
    #print('Influences',influences)
    #print('Influenced',influenced)
    
scrape('https://en.wikipedia.org/wiki/Adam_Smith',0)
#scrape('https://en.wikipedia.org/wiki/Hassan_al-Banna',0)
#scrape('https://en.wikipedia.org/wiki/Sayyid_Qutb',0)
#scrape('https://en.wikipedia.org/wiki/Plato',0)
print('Influences',influences)
print('Influenced',influenced)

f = open("adjacency_list.txt", "w")
for person in scraped:
    str = '"'+person+'" '
    connections = set()
    for influencer in influences:
        connections.add(influencer)
    for influencee in influenced:
        connections.add(influencee)
    for connection in connections:
        str = str + ' "' + connection + '"'
    f.write(str+'\n')
f.close()