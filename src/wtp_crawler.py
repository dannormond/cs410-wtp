#!/usr/env python

import argparse
import pickle
import urllib 
from bs4 import BeautifulSoup, Comment
import re
import json
from wtp_data import Petition, PetitionEncoder

BASE_URL = 'https://petitions.whitehouse.gov'
PEITION_LIST_URL = BASE_URL + '/petitions/all/{0}/1/0'

def listPetitions():
    PETITION_PAGES = 8
    petitions = []
    for i in range(1, PETITION_PAGES+1):
        url = PEITION_LIST_URL.format(i)
        print("Getting Threads for ", url)
        page = urllib.urlopen(url)
        #data = page.read()
        #print(data)

        bs = BeautifulSoup(page, 'html5lib')
        #print (bs.prettify())
        for petition_div in bs.find_all('div', id=re.compile('petition-[0-9]')):
            petition_title_link = petition_div.find(class_='title').a
            petition_title = petition_title_link.string
            petition_url = BASE_URL + petition_title_link['href']
            petition_sigs = int(petition_div.find(class_='num-sig').span.string.replace(',', ''))

            petition = Petition(petition_url, petition_title, petition_sigs)
            petitions.append(petition)
    return petitions            

def getContent(threads):
    pageContents = {}
    for (url, title) in threads.items():
        title = title.encode('ascii', 'ignore')
        print("Getting content for ", title)
        page = urllib.urlopen(url)
        bs = BeautifulSoup(page, 'lxml')

        # string all comments
        comments = bs.findAll(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        contentTag = bs.find(id='posts')
        divs = contentTag.find_all('div')
        contentStr = ''
        for div in divs:
            id = div.get('id')
            if (id != None and
                id.startswith('post_message')):
                contentStr = contentStr + ' '.join(div.find_all(text=True))
        pageContents[url] = contentStr.encode('ascii', 'ignore')
    return pageContents

def crawl():
    petitions = listPetitions()
    
    print(PetitionEncoder().encode(petitions))

def main():
    argParser = argparse.ArgumentParser(
        description='A Crawler for a specific forum')
    argParser.add_argument('-a', '--action', choices=['crawl', 'xml'], required=True,
        help='Specify the action to either crawl the form or to generate xml from a previous crawl')
    args = argParser.parse_args()

    if args.action == 'crawl':
        # crawl the form
        print("Crawling the Forum")
        crawl()
    elif args.action == 'xml':
        # generate xml from the previous crawl
        print("Generating Solr XML")
        genxml()

    #
    #createXML(threads, content)

if __name__ == "__main__":
    main()
