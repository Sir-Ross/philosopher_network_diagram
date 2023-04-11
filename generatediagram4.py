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
names = set()
dict_of_people = defaultdict(set)

#f1 = open("influences.txt", "w", encoding="utf-8")
#f2 = open("influenced.txt", "w", encoding="utf-8")
#f1.write("")
#f2.write("")
#f1.close()
#f2.close()


def getSoup(r):
    return BeautifulSoup(r.content, "lxml", from_encoding="utf-8")

@persist_to_file('cache.dat')
def getName(link):
    if link.startswith("https://en.wikipedia.org/wiki"):
        try:
            r = requests.get(link)
        except:
            print("Error in getName("+link+")\n")
            #raise
            return
        
        soup = getSoup(r)
        if soup.find('span', class_='mw-page-title-main'):
            return soup.find('span', class_='mw-page-title-main').text
        else:
            return link.replace('https://en.wikipedia.org/wiki/','')
    #else:
        #print(link)
        #return


def scrape(link,n):
    
    if not link.startswith("https://en.wikipedia.org/wiki"):
        print(link)
        return
    try:
        r = requests.get(link)
    except:
        print("Error in scrape("+link+","+n+") \n")
        #raise
        return
            
    soup = getSoup(r)
    page_name = getName(link)
    if page_name == "Citation needed":
        return
    if page_name not in scraped:
        #f1 = open("influences.txt", "a", encoding="utf-8")
        #f2 = open("influenced.txt", "a", encoding="utf-8")
        #print(n*'.'+'"'+page_name+'"')
        #return
        scraped.append(page_name)
        
        influences = []
        influenced = []
        
        if soup.find('div', string='Influences'):
            print('\n'+str(len(scraped))+'\t'+(n*' ')+'"'+page_name+'" < ',end='')
            #f1.write('"'+page_name+'"')
            for child in soup.find('div', string='Influences').parent.descendants:
                if child.name == 'a':
                    # child['href'] is the link to the influence
                    # Add to adjacency list by webpage name and recurse if the person is new
                    if child.get('href'):
                        if child['href'].startswith('/wiki/'):
                            influencer_link = 'https://en.wikipedia.org' + child['href']
                            influencer = getName(influencer_link)
                            if influencer == 'Main Page':
                                continue
                            if influencer != "":
                                #f1.write(' "'+influencer+'"')
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
            print('\n'+str(len(dict_of_people[page_name]))+'\t'+(n*' ')+'"'+page_name+'" > ',end='')
            #f2.write('"'+page_name+'"')
            for child in soup.find('div', string='Influenced').parent.descendants:
                if child.name == 'a':
                    # child['href'] is the link to the influence
                    # Add to adjacency list by webpage name and recurse if the person is new
                    if child.get('href'):
                        if child['href'].startswith('/wiki/'):
                            influencee_link = 'https://en.wikipedia.org' + child['href']
                            influencee = getName(influencee_link)
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
            
scrape('https://en.wikipedia.org/wiki/Adam_Smith',0)

f = open("adjacency_list.txt", "w")
for n in scraped:
    f.write('"'+n+'"')
    for i in dict_of_people[n]:
        f.write(' "'+i+'"')
    f.write('\n')
f.close()
    