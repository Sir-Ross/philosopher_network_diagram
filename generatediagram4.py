import requests
from bs4 import BeautifulSoup
import sys
import queue
import functools
import json, atexit
from collections import defaultdict

def persist_to_file(file_name):

    try:
        cache = json.load(open(file_name, 'r'))
    except (IOError, ValueError):
        cache = {}

    atexit.register(lambda: json.dump(cache, open(file_name, 'w')))

    def decorator(func):
        def new_func(param):
            if param not in cache:
                cache[param] = func(param)
            return cache[param]
        return new_func

    return decorator

scraped = []
detailed = []
names = set()
dict_of_people = defaultdict(set)
#dict_of_detail = defaultdict(defaultdict(set))
f_detail = open("detail.csv", "w")
f_detail.write("Label,Type,Region,Era\n")
f_detail.close()

#influences = []
#influenced = []
#f1 = open("influences.txt", "w", encoding="utf-8")
#f2 = open("influenced.txt", "w", encoding="utf-8")
#f1.write("")
#f2.write("")
#f1.close()
#f2.close()

#@persist_to_file('cache_new.dat')
def getSoup(link):
    try:
        r = requests.get(link)
    except:
        print("Error in getName("+link+")\n")
        #raise
        return
    return BeautifulSoup(r.content, "lxml", from_encoding="utf-8")

@persist_to_file('cache_new_getName.dat')
def getName(link):
    if link.startswith("https://en.wikipedia.org/wiki"):
        soup = getSoup(link)
        if not soup:
            return
        out_name = ""
        era = ""
        region = ""
        school = ""
        
        #f_detail = open("detail.csv", "a")
        if soup.find('span', class_='mw-page-title-main'):
            out_name = soup.find('span', class_='mw-page-title-main').text.replace(',','')
        else:
            out_name = link.replace('https://en.wikipedia.org/wiki/','').replace(',','')
            
        era_tag = soup.find('th', class_="infobox-label", string="Era")
        if era_tag:
            for child in era_tag.next_sibling.descendants:
                if child.name == 'a':
                    era = child.string.replace(',','')
                    break
        
        region_tag = soup.find('th', class_="infobox-label", string="Region")
        if region_tag:
            for child in region_tag.next_sibling.descendants:
                if child.name == 'a':
                    region = child.string.replace(',','')
                    break
                    
        school_tag = soup.find('th', class_="infobox-label", string="School")
        if school_tag:
            for child in school_tag.next_sibling.descendants:
                if child.name == 'a':
                    school= child.string.replace(',','')
                    break
        
        #f_detail.write(out_name+","+school+","+region+","+era+"\n")
        
        #f_detail.close()
        if out_name not in detailed and out_name not in scraped:
            f_detail = open("detail.csv", "a")
            f_detail.write(out_name+","+school+","+region+","+era+"\n")
            
            f_detail.close()
            
        detailed.append(out_name)
        return ({'name':out_name,'school':school,'region':region,'era':era})
    else:
        #print(link)
        return 

#@persist_to_file('cache_parse.dat')
#def parselink(link):


def scrape(link, n):
    if not link.startswith("https://en.wikipedia.org/wiki"):
        print(link)
        return
        
    try:
        r = requests.get(link)
    except:
        print("Error in parselink("+link+") \n")
        #raise
        return
            
    soup = getSoup(link)
    data = getName(link)
    #print(data)
    if not data:
        return
    page_name = str(data['name'])
    school = str(data['school'])
    region = str(data['region'])
    era = str(data['era'])
    #page_name = getName(link)
         
        
    #print(type(page_name))
    #print(type(dict_of_people))
    if page_name == "Citation needed":
        return
    if page_name not in scraped:
        
        #f1 = open("influences.txt", "a", encoding="utf-8")
        #f2 = open("influenced.txt", "a", encoding="utf-8")
        #print(n*'.'+'"'+page_name+'"')
        #return
        scraped.append(page_name)
        
        influences = list()
        influenced = list()
        
        if soup.find('div', string='Influences'):
            print('\n'+str(len(scraped))+'\t"'+page_name+'" < ',end='')
            #f1.write('"'+page_name+'"')
            for child in soup.find('div', string='Influences').parent.descendants:
                if child.name == 'a':
                    # child['href'] is the link to the influence
                    # Add to adjacency list by webpage name and recurse if the person is new
                    if child.get('href'):
                        if child['href'].startswith('/wiki/'):
                            influencer_link = 'https://en.wikipedia.org' + child['href']
                            influencer = getName(influencer_link)['name']
                            if influencer == 'Main Page':
                                continue
                            if influencer != "":
                                #f1.write(' "'+influencer+'"')
                                #print(type(page_name),type(influencer))
                                dict_of_people[page_name].add(influencer)
                                print(' "'+influencer+'"',end='')
                                if not (influencer_link in scraped):
                                    influences.append(influencer_link)
                                #influences.setdefault(page_name,[])
                                #influences[page_name].append(influencer)
                                #if not (influencer in influences.keys()):
                                    #print(">", end = '')
                                    #scrape(influencer_link,n+1)
                        #else:
                            #print('\n',child['href'])
            #f1.write('\n')
        
        if soup.find('div', string='Influenced'):
            print('\n'+str(len(dict_of_people[page_name]))+'\t"'+page_name+'" > ',end='')
            #f2.write('"'+page_name+'"')
            for child in soup.find('div', string='Influenced').parent.descendants:
                if child.name == 'a':
                    # child['href'] is the link to the influence
                    # Add to adjacency list by webpage name and recurse if the person is new
                    if child.get('href'):
                        if child['href'].startswith('/wiki/'):
                            influencee_link = 'https://en.wikipedia.org' + child['href']
                            influencee = getName(influencee_link)['name']
                            if influencee == 'Main Page':
                                continue
                            if influencee != "":
                                #f2.write(' "'+influencee+'"')
                                dict_of_people[influencee].add(page_name)
                                print(' "'+influencee+'"',end='')
                                if not (influencee_link in scraped):
                                    influenced.append(influencee_link)

                            #influences.setdefault(page_name,[])
                            #influences[page_name].append(influencer)
                            #if not (influencer in influences.keys()):
                                #print(">", end = '')
                                #scrape(influencer_link,n+1)
                    #else:
                        #print('\n',child['href'])
        #f2.write('\n')
        
    #f1.close()
    #f2.close()
    
        while len(influences)!=0:
            scrape(influences.pop(0),n+1)
        while len(influenced)!=0:
            scrape(influenced.pop(0),n+1)
            
scrape('https://en.wikipedia.org/wiki/Adam_Smith', 0)

f = open("adjacency_list.txt", "w")
for n in scraped:
    f.write('"'+n+'"')
    for i in dict_of_people[n]:
        f.write(' "'+i+'"')
    f.write('\n')
f.close()
    