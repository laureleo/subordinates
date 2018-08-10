# crawler designed for the facebook group LAUSANNE à louer - bouche à oreille at https://www.facebook.com/groups/330486193693264/
# since it's way too slow to sort through the content manually
import os
import bs4
import re
import requests
import json
import datetime as dt
from requests.compat import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#On using selenium http://stanford.edu/~mgorkove/cgi-bin/rpython_tutorials/Scraping_a_Webpage_Rendered_by_Javascript_Using_Python.php
"""
@funct: takes an url, stores a copy of the site locally by downloading its html and a copy of all of the resources it links to.
@param: an url
"""
def update(url):
    print("Creating a directory to store the results in")
    make_directory(url)

    print("Loading mother page")
    response = get_response_object(url)

    print("Extracting urls to all objects for sale")
    links = regex_links(response)

    articles = []
    for i, link in enumerate(links):
        print("Loading article {}. Extracting content...".format(i+1))
        html = get_js_content_headless(link)
        #html = get_js_content(link)
        article = make_article(html, link)
        articles.append(article)

    print("Storing all articles...")
    filename = str(dt.datetime.now())
    with open(filename + ".json", "w+") as write_file:
            json.dump(articles, write_file)

def make_article(html, url):
    title, price, place, time, description = extract_content(html)

    article = {
            "title": title,
            "price": price,
            "place": place,
            "time": time,
            "description": description,
            "url": url
            }

    return article


def get_js_content_headless(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    outer_html = browser.page_source
    inner_html = browser.execute_script("return document.body.innerHTML")
    return inner_html

def get_js_content(url):
    browser = webdriver.Chrome()
    browser.get(url)
    outer_html = browser.page_source
    inner_html = browser.execute_script("return document.body.innerHTML")
    return(inner_html)

def regex_links(response):
    urls = []
    if response:
        html = response.text
        link_pattern = "\/groups\/\d*?\/permalink\/\d*?\/\?(?=sale_post)"
        regex = re.compile(link_pattern, re.IGNORECASE)
        matches = re.findall(regex, html)
        for match in matches:
            match = "https://www.facebook.com" + match
            urls.append(match)
        urls = list(set(urls))
        print("extracted {} links from the page".format(len(urls)))
    return urls

def extract_content(html):
    soup = bs4.BeautifulSoup(html, 'html5lib')

    title = soup.find('div',
            attrs = {'class': '_l53'})
    if not title:
        title = 'N/A'
    else:
        title = title.text

    price = soup.find('div',
            attrs = {'class': '_l57'})
    if not price:
        price = 0
    else:
        price = calculate_price(price)
        
    location = soup.find('div',
            attrs = {'class': '_l58'})
    if not location:
        location = 'N/A'
    else:
        location = location.text

    description = soup.find('div',
            attrs = {'class': '_5pbx userContent _3576'})
    if not description:
        description = 'N/A'
    else:
        description = description.text

    time = soup.find('abbr',
            attrs = {'class': '_5ptz'})
    if not time:
        time = "N/A"
    else:
        time = calculate_time(time)

    return(title, price, location, time, description)

def calculate_price(price):
    text = price.text
    numbers = re.sub("\D", "", text) 
    price = int(float(numbers) * 9.06)
    return price

def calculate_time(time):
    text = time.get('title')
    # this was the case when running witout the headless at lest match = re.search('(?P<dd>\d+)\/(?P<mm>\d+)\/(?P<yyyy>\d+)\s(?P<hh>\d+):(?P<m2>\d+)', text)
    match = re.search('(?P<yyyy>\d+)-(?P<mm>\d+)-(?P<dd>\d+)\s(?P<hh>\d+):(?P<m2>\d+)', text)
    dd = int(match.group('dd'))
    mm = int(match.group('mm'))
    yyyy = int(match.group('yyyy'))
    hh = int(match.group('hh'))
    m2 = int(match.group('m2'))

    date_article = dt.datetime(yyyy, mm, dd, hh, m2)
    date_today = dt.datetime.today()
    diff = date_today-date_article
    time_elapsed = diff.days
    
    return time_elapsed


"""
@funct: creates a folder to contain all the content consumed and moves the execution process into that folder
@param: an url
"""
def make_directory(url):
    directory = "./" + url.split('/')[-1]
    try:
        os.makedirs(directory)
        print("Directory created")
    except Exception as exc:
        print("Notification: %s" %(exc))

    os.chdir(directory)


""" 
@funct: creates a response object while dealing with errors
@param: an URL
@retur: a response object
"""
def get_response_object(url):
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






update("https://www.facebook.com/groups/330486193693264/forsaleposts/?story_id=2097041673704365")
