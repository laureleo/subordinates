#Downloads a link and the content linked to from that page
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
    mkdir(url)
    response = get_response(url)
    clone_content(response)
    urls = extract_urls(response)
    for url in urls:
        response = get_response(url)
        clone_content(response)
    print("It was delicious")


"""
@funct: creates a folder to contain all the content consumed and moves the execution process into that folder
@param: an url
"""
def mkdir(url):
    directory = "./" + url.split('/')[-1]
    try:
        os.makedirs(directory)
        print("Directory created")
    except Exception as exc:
        print("Notification: %s" %(exc))

    os.chdir(directory)


""" 
@funct: creates a local copy of the content existing at the specified url
@param: an URL
@retur: a response object
"""
def get_response(url):
    try:
        response = requests.get(url)
        return response
    except Exception as exc:
        print("Notification: %s" %(exc))



"""
@funct: stores a local copy of the content found in the response object
@param: a response object
"""
def clone_content(response):
    if response:
        url = response.url
        if url[-1] == '/':
            url = url[:-1]
        filename = url.split('/')[-1] 
        if 'text/html' in response.headers['content-type']:
            filename = filename + '.html'
        try:
            copy = open(filename, 'wb+')
            for chunk in response.iter_content(1024):
                copy.write(chunk)
            copy.close()
            print("downloaded " + filename)
        except Exception as exc:
            print("Notification: %s" %(exc))



"""
@funct: checks if the object is html/text. If it is, it returns all urls found in it
@param: a response object
@retur: a list of urls
"""
def extract_urls(response):
    urls = []
    if response:
        if 'text/html' in response.headers['content-type']:
            soup = bs4.BeautifulSoup(response.content, 'html5lib')
            links = soup.findAll('a')
            for link in links:
                link = link.get('href')
                link = urljoin(response.url, link) # Makes relative urls absolute
                urls.append(link)
            #In case of duplicates, remove them
            urls = set(urls)
            print("Found {} links".format(len(urls)))
    return urls



#consume('https://www.youtube.com/watch?v=9bZkp7q19f0')
#consume('http://www-personal.umich.edu/~csev/books/py4inf/media/Py4Inf-01-Intro.pdf')
consume('https://www.facebook.com/groups/330486193693264')
