#!/usr/env python

import argparse
import urllib 
from bs4 import BeautifulSoup, Comment
import re
import json
import wtp_data
import datetime

BASE_URL = 'https://petitions.whitehouse.gov'
PEITION_LIST_URL = BASE_URL + '/petitions/all/{0}/1/0'

def listPetitions():
    PETITION_PAGES = 1
    petitions = []
    for i in range(1, PETITION_PAGES+1):
        url = PEITION_LIST_URL.format(i)
        print "Getting Petitions on ", url
        page = urllib.urlopen(url)
        #data = page.read()
        #print(data)

        bs = BeautifulSoup(page, 'html5lib')
        #print (bs.prettify())
        for petition_div in bs.find_all('div', id=re.compile('petition-[0-9]')):
            petition_title_link = petition_div.find(class_='title').a
            petition_title = petition_title_link.string
            petition_url = BASE_URL + petition_title_link['href']
            petition_sigs = [int(petition_div.find(class_='num-sig').span.string.replace(',', ''))]

            petition = wtp_data.Petition(petition_url, petition_title, petition_sigs)
            getContent(petition)
            petitions.append(petition)
    return petitions

def getContent(petition):
    petition_page = urllib.urlopen(petition.id)
    bs = BeautifulSoup(petition_page, 'html5lib')
    petition_detail = bs.find(id='petition-detail')
    petition_text = ""
    for p in petition_detail.find_all('p'):
        if (p.string is not None):
            petition_text += p.string + "\n"

    petition_date = petition_detail.find('div', class_='date')
    for string in petition_date.stripped_strings:
        if not string.startswith("Created"):
            creation_date = datetime.datetime.strptime(string, "%b %d, %Y")
            petition.creation_date = creation_date.strftime("%Y-%m-%d")

    petition.text = petition_text
    

def crawl():
    return listPetitions()

def load_petitions(file_name):
    try:
        with open(file_name, 'r') as f:
            petitions = json.load(f, object_hook=wtp_data.load_hook)

        for p in petitions:
            print str(p)

        return petitions
    except IOError:
        return []

def update_petitions(petitions, updated_petitions):
    petition_set = set(petitions)
    updates_set = set(updated_petitions)

    new_petitions = updates_set - petition_set
    # intersection is petitions that need updating
    updated_petitions_set = petition_set & updates_set

    # Update the petitions signature
    for petition in updated_petitions_set:
        orig_petition = wtp_data.get_eq(petitions, petition)
        update_petition = wtp_data.get_eq(updates_set, petition)
        
        sigs = update_petition.signatures.pop()
        orig_petition.signatures.append(sigs)

    # Add new petitions to the petition list
    for petition in new_petitions:
        petitions.append(petition)

def save_petitions(petitions, file_name):
    try:
        with open(file_name, 'w') as f:
            f.write(wtp_data.as_json(petitions))
    except IOError:
        print "Unable to open file", file_name

def main():
    argParser = argparse.ArgumentParser(
        description='A Crawler for a specific forum')
    argParser.add_argument('-f', '--file', required=False, default="../data/wtp.json",
        help='File to use during updating and saving')
    args = argParser.parse_args()

    print "Crawling WTP"
    crawled_petitions = crawl()
    print("Loading data from " + args.file)
    petitions = load_petitions(args.file)

    print "Crawled Petitions:", len(crawled_petitions)
    print "Loaded Petitions:", len(petitions)

    print("Updating petitions");
    update_petitions(petitions, crawled_petitions)
    print("Saving petitions to " + args.file)
    save_petitions(petitions, args.file)

if __name__ == "__main__":
    main()
