import os
from bs4 import BeautifulSoup
import requests
import re
import json
# x-axis = year of journal inception date
# y-axis = number of journals published that year
# line = one per field (where field is defined by wikipedia)

# 1. create dictionary: <field> <year> <name of journal

# 2. sum a groupby field, year as a third column; i.e. <field> <year> <num journals per year>

################# GET WIKIPEDIA LINKS TO EACH JOURNAL PAGE #################
base_url = "http://en.wikipedia.org"
link_ending_full_journal_list = "/wiki/List_of_scientific_journals"
# These are the journal links directly on this page: http://en.wikipedia.org/wiki/List_of_scientific_journals
def get_wiki_journal_links(link_ending):

    url = "".join([base_url, link_ending])

    try:
        c = requests.get(url).content
    except Exception:
        print(url)
        c = ""
    soup = BeautifulSoup(c)
    links = soup.select('ul > li > i > a')
    
    #print(url)
    journal_urls = ["".join([base_url, x['href']]) for x in links]

    return journal_urls

# These catch and get the journal links on the list per sub-field
def get_wiki_subfield_journal_links(journal_links=[]):

    # part one: get the wiki pages for sublists
    #base_url = "http://en.wikipedia.org"
    url = "".join([base_url, "/wiki/List_of_scientific_journals"])
    soup = BeautifulSoup(requests.get(url).content)
    links = soup.select('.hatnote a')
    one_more = soup.select("dl > dd > i > a")
    links.append(one_more[0])
    
    u = [x['href'] for x in links]
    
    #part two: parse out the links from the pages
    for end_url in u:
        if end_url[:6] == "/wiki/":
            #print(end_url)
            journal_links += (get_wiki_journal_links(end_url))
    
    return journal_links
###########################################################################


################# PARSE EACH WIKIPEDIA JOURNAL PAGE #################
def create_database_file(url_list, filepath,logpath):
    #url = "http://en.wikipedia.org/wiki/Journal_of_the_American_Statistical_Association"
    print("creating database file form url list: %s, with log: %s" % (filepath,logpath))
    with open(filepath, 'w') as csv:
        csv.write("journal_name,discipline,inception_year,year_range,impact_factor,journal_link,description\n")
        for url in url_list:
            
            

            try:
                c = requests.get(url).content
            except Exception:
                print(url)
                c = ""
            soup = BeautifulSoup(c)

            try:

                journal_info_table = soup.select('#mw-content-text table.infobox')[0]
                journal_name = journal_info_table.select('span.fn')[0].text

                table_info = journal_info_table.find_all("td")
                discipline = journal_info_table.find_all("td", {"class": "category"})[0].find_all('a')[0].text
                year_range = get_inception_date(journal_info_table)#table_info[5].text.split('–')[0] # NOTE: this is not a normal dash; copied directly from site               
                inception_year = year_range[:4]
                #impact_factor = table_info[7].text
                #journal_link = [x['href'] for x in journal_info_table.find_all('a', href=True, text="Journal homepage")][0]
                #description = soup.select('#mw-content-text > p')[0].text
                print("exits %s " % url)
                csv.write(",".join([journal_name,discipline,inception_year+"\n"]))
            
            except Exception:
                #print(Exception)
                #try:

                #    t = soup.find('p').text
                #except Exception:
                #    t = "something went wrong"
                with open(logpath,'a') as log:
                    print("does not: %s " % url)
                    log.write(url + '\n')

def get_inception_date(soup):
    rows = soup.find("div", text="Publication history")
    inception_date = rows.parent.parent.td.text
    return inception_date

if __name__ == "__main__":
    #shortlist = get_wiki_journal_links(link_ending_full_journal_list)
    longlist = get_wiki_subfield_journal_links()
    create_database_file(longlist,"/Users/emma/Documents/hackerschool/history-of-science/journal_db.csv",
                                  "/Users/emma/Documents/hackerschool/history-of-science/logfile.txt")


# i have a feeling i don't need both the short and the long list; check if everything on the short list is on the long list
# debug the logfile for why i couldn't grab all the information from each of the pages (some don't ahve it, but some do! why not get it!)
# change delimiter
