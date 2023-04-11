import requests
from bs4 import BeautifulSoup
import sys
import queue

scraped = []
names = set()

f1 = open("influences.txt", "w")
f2 = open("influenced.txt", "w")
f1.write("")
f2.write("")
f1.close()
f2.close()



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
        #print(link)
        return ""
        
def scrape(link,n):
    f1 = open("influences.txt", "a")
    f2 = open("influenced.txt", "a")
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
    scraped.append(link)
    
    
    
    
    influences = []
    influenced = []
    
    if soup.find('div', string='Influences'):
        print('\n\t'+(n*' ')+'"'+page_name+'" < ',end='')
        f1.write('"'+page_name+'"')
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
                        f1.write(' "'+influencer+'"')
                        print(' "'+influencer+'"',end='')
                        if not (influencer_link in scraped):
                            influences.append(influencer_link)
                        #influences.setdefault(page_name,[])
                        #influences[page_name].append(influencer)
                        #if not (influencer in influences.keys()):
                            #print(">", end = '')
                            #scrape(influencer_link,n+1)
        f1.write('\n')
    
    if soup.find('div', string='Influenced'):
        print('\n\t'+(n*' ')+'"'+page_name+'" > ',end='')
        f2.write('"'+page_name+'"')
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
                        f2.write(' "'+influencee+'"')
                        print(' "'+influencee+'"',end='')
                        if not (influencee_link in scraped):
                            influenced.append(influencee_link)
                        #influences.setdefault(page_name,[])
                        #influences[page_name].append(influencer)
                        #if not (influencer in influences.keys()):
                            #print(">", end = '')
                            #scrape(influencer_link,n+1)
        f2.write('\n')
        
    f1.close()
    f2.close()
    
    while len(influences)!=0:
        scrape(influences.pop(0),n+1)
    while len(influenced)!=0:
        scrape(influenced.pop(0),n-1)
        
scrape('https://en.wikipedia.org/wiki/Adam_Smith',0)

