import os
from bs4 import BeautifulSoup
import requests
import re
import json


# problems:
# there are 172 journals in first pass through, but 136 of them don't seem to have a publication date...?

# part 1: grab the main list from wikipedia (later: grab the longer lists that are on this page)
#		--> get a list of urls to the wiki page for each journal

def get_wiki_journal_links():

	base_url = "http://en.wikipedia.org"
	url = "/".join([base_url, "wiki/List_of_scientific_journals"])
	soup = BeautifulSoup(requests.get(url).text)
	links = soup.select('#mw-content-text > ul > li > i > a')
	journal_urls = ["".join([base_url, x['href']]) for x in links]

	return journal_urls

#journal_list_html = soup.find_all("a", href=re.compile("/wiki/"))
#journal_urls = ["".join([base_url, x['href']]) for x in journal_list_html]

def create_journal_list():

	journal_url_shortlist = get_wiki_journal_links()
	journal_list = [] # a list of journal objects

	for url in journal_url_shortlist:
		journal_list.append(create_journal_object(url))

	print("there are %d journals" % len(journal_list))

	return journal_list
# part 2: visit each page and grab: discipline, publication history, impact factor (if exists), desc, 

def create_journal_object(url):
	#url = "http://en.wikipedia.org/wiki/Journal_of_the_American_Statistical_Association"
	soup = BeautifulSoup(requests.get(url).text)
	try:
		journal_info_table = soup.select('#mw-content-text table.infobox')[0]
		journal_name = journal_info_table.select('span.fn')[0].text
		table_info = journal_info_table.find_all("td")
		discipline = journal_info_table.find_all("td", {"class": "category"})[0].find_all('a')[0].text
		year_range = get_inception_date(journal_info_table)#table_info[5].text.split('–')[0] # NOTE: this is not a normal dash; copied directly from site
		inception_year = year_range[:4]
		impact_factor = table_info[7].text
		journal_link = [x['href'] for x in journal_info_table.find_all('a', href=True, text="Journal homepage")][0]
		description = soup.select('#mw-content-text > p')[0].text

		return Journal(journal_name, discipline, inception_year, year_range, impact_factor, journal_link, description)
	
	except Exception:
		#print(Exception)
		t = soup.find('p').text
		return Journal(name = url, description=t)



class Journal():

	def __init__(self, name, field = None, inception_year = None, 
					year_range = None, impact_factor = None,
					link = None, description = None, papers = None):
		self.name = name
		self.field = field
		self.inception_year = inception_year
		self.year_range = year_range
		self.link = link
		self.description = description
		self.papers = papers

	def get_json(self):
		#todo
		print("need to write this function still")

	def get_property_list(self):
		if (self.field != None):
			return [self.name, self.field, self.inception_year, self.link, self.papers]
		else:
			return [self.name, self.description]

	def __repr__(self):
		return self.name


def get_inception_date(soup):
	rows = soup.find("div", text="Publication history")
	inception_date = rows.parent.parent.td.text
	return inception_date

def generate_json_obj(journal_list):

	all_journals = {}
	for j in journal_list:

		data = {}
		data['name'] = j.name
		data['field'] = j.field
		data['inception_year'] = j.inception_year
		data['year_range'] = j.year_range
		data['link'] = j.link
		data['description'] = j.description
		all_journals[j.name] = data

	json_data = json.dumps(all_journals, indent=4, sort_keys=True)
	return json_data


if __name__ == "__main__":
	jl = create_journal_list()
	json_obj = generate_json_obj(jl)
	with open('json_test.html','w') as f:
		f.write(json_obj)

	#url = "http://en.wikipedia.org/wiki/Journal_of_the_American_Statistical_Association"
	#soup = BeautifulSoup(requests.get(url).text)
	#i_date = get_inception_date(soup)
	#print(i_date)
#just_info = {}
#for row in journal_info_table.find_all("tr"):
#	aux = row.find_all("td")
#	if aux != [] and len(aux)>1:
#		just_info[aux[0].text] = aux[1].text
#table_info=journal_info_table.find_all("td")
#print(journal_urls)
#print(just_info)
# for a more comprehenisve list ... --> eventually scrape these
# on each journal's wikipedia page, scrape:
	# Discipline
	# Publication history
	# Impact factor (maybe)
	# The first line in the thing (for readability purposes)
	# link to journal homepage (for future use in "second depth" )


# second depth:
	# get the authors that have published in these journals
		# --> going to have to scrape the journal websites I think...

#print(soup.prettify())
#def grab_sci_journals_from_wikipedia():


# jquery $(" // css selector

	# dcitonary on how to get it; and then use that
