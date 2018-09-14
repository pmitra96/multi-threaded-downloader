import requests
from bs4 import BeautifulSoup
import sys
from googlesearch.googlesearch import GoogleSearch

######################################################################################
# BS CODE NOT REQUIRED
def exp(url):
	hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
	page = requests.get(url,headers=hdr).content
	soup = BeautifulSoup(page)
	soup.prettify()
	for anchor in soup.find_all(class_="blog-carousel"):
		for i in anchor.find_all('a',href=True):
			try:
				has_download(i['href'])
			except:
				pass

def has_download(url):
	hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
	page = requests.get(url,headers=hdr).content
	soup = BeautifulSoup(page)
	soup.prettify()
	for anchor in soup.findAll('a', href=True)[1::]:
		print "has_download " + anchor["href"]
#######################################################################################

def g_search(query):
	response = GoogleSearch().search("index of " + query)
	return response.results

	    

if __name__ == "__main__":
	print sys.argv
	g_search(sys.argv[1])