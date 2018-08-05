#Given an url, downloads a webpage perfectly.
import os
import bs4
import requests
from requests.compat import urljoin

"""
@funct: takes an url, stores a copy of the site locally by downloading its html and a copy of all of the resources it links to.
@param: an url
"""
def consume(url):
    print("Time to eat {}".format(url))
 #   response = get_response(url)
 #   clone_content(response)
 #   urls = extract_urls(response)
 #   for url in urls:
 #       get_response(url)

    print(os.getcwd())
    os.makedirs("./" + url.split('/')[-1])
    print("It was delicious")


""" 
@funct: creates a local copy of the content existing at the specified url
@param: an URL
@retur: a response object
"""
def get_response(url):
    response = requests.get(url)
    try:
        response.raise_for_status()
    except Exception as exc:
        print("ERROR: %s" %(exc))

    return response

"""
@funct: stores a local copy of the content found in the response object
@param: a response object
"""
def clone_content(response):
    filename = response.url.split('/')[-1] 
    if 'text/html' in response.headers['content-type']:
        filename = filename + '.html'
    copy = open(filename, 'wb+')
    for chunk in response.iter_content(1024):
        copy.write(chunk)
    copy.close()



"""
@funct: checks if the object is html/text. If it is, it returns all urls found in it
@param: a response object
@retur: a list of urls
"""
def extract_urls(response):
    urls = []
    if 'text/html' in response.headers['content-type']:
        soup = bs4.BeautifulSoup(response.content, 'html5lib')
        links = soup.findAll('a')
        for link in links:
            link = link.get('href')
            link = urljoin(response.url, link) # Makes relative urls absolute
            urls.append(link)
        #In case of duplicates, remove them
        urls = set(urls)
    return urls



#consume('https://imgur.com/gallery/U2DdZ4y')
consume('https://www.youtube.com/watch?v=9bZkp7q19f0')
#consume('http://www-personal.umich.edu/~csev/books/py4inf/media/Py4Inf-01-Intro.pdf')
#consume('http://www-personal.umich.edu/~csev/books/py4inf/media')

