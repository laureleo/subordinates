# crawler designed for the facebook group LAUSANNE à louer - bouche à oreille at https://www.facebook.com/groups/330486193693264/
# since it's way too slow to sort through the content manually
import os
import bs4
import re
import requests
import json
import datetime as dt
import glob
import time
from requests.compat import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
#On using selenium http://stanford.edu/~mgorkove/cgi-bin/rpython_tutorials/Scraping_a_Webpage_Rendered_by_Javascript_Using_Python.php
#TODO: Read existing json into memory. 
"""
@funct: takes an url, stores a copy of the site locally by downloading its html and a copy of all of the resources it links to.
@param: an url
"""
def update(url):
    print("You are running update. This will create a new json object of all articles found on the website.")
    print("You should probably make it so previously visited urls aren't re-visited sometime. Maybe")
    print("Creating a directory to store the results in")
    make_directory(url)

    print("Loading mother page")
    start_page = get_js_content_headless(url, True)

    print("Extracting urls to all objects for sale")
    links = regex_links(start_page)

    articles = []
    for i, link in enumerate(links):
        print("Loading article {}. Extracting content...".format(i+1))
        try:
            html = get_js_content_headless(link, False)
            article = make_article(html, link)
            articles.append(article)
        except Exception as exc:
            print("Notification: Skipping this article  %s" %(exc))
            print(link)

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


def get_js_content_headless(url, scroll):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    try:
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        if scroll is True: 
            lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match=False
            count = 0
            while(match==False):
                count = count + 1
                print("Scrolled to the bottom {} times...".format(count))
                lastCount = lenOfPage
                time.sleep(0.5)
                lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                    match=True

        outer_html = browser.page_source
        inner_html = browser.execute_script("return document.body.innerHTML")
        browser.close()

    except TimeoutException as ex:
        print("Exception has been thrown. " + str(ex))
        browser.close()
    return inner_html

def get_js_content(url):
    browser = webdriver.Chrome()
    browser.get(url)
    outer_html = browser.page_source
    inner_html = browser.execute_script("return document.body.innerHTML")
    return(inner_html)

def regex_links(html):
    urls = []
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
    try:
        price = int(float(numbers) * 9.06)
    except Exception as exc:
        print("Notification: %s" %(exc))
        print("Did not manage to deal with {} converted to {}".format(text, numbers))
        price = 0


    return price

def calculate_time(time):
    text = time.get('title')
    # this was the case when running witout the headless at lest match = re.search('(?P<dd>\d+)\/(?P<mm>\d+)\/(?P<yyyy>\d+)\s(?P<hh>\d+):(?P<m2>\d+)', text)
    match = re.search('(?P<yyyy>\d+)-(?P<mm>\d+)-(?P<dd>\d+)\s(?P<hh>\d+):(?P<m2>\d+)', text)
    try:
        dd = int(match.group('dd'))
        mm = int(match.group('mm'))
        yyyy = int(match.group('yyyy'))
        hh = int(match.group('hh'))
        m2 = int(match.group('m2'))

        date_article = dt.datetime(yyyy, mm, dd, hh, m2)
        date_today = dt.datetime.today()
        diff = date_today-date_article
        time_elapsed = diff.days
    
    except Exception as exc:
        print("Notification: %s" %(exc))
        print("Something went wrong with the time conversion. The string that failed was {}".format(text))
        print("Setting time to 0")
        time_elapsed = 0
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

def run(url, command, p_range = [0, 50000], t_range = [0, 1000]):
    print("Loading the latest saved copy of articles found in the folder...")
    articles = load_latest(url)
    print("{} articles found".format(len(articles)))
    print("Showing all results with a cost between {} and {} SEK published between {} and {} days ago".format(p_range[0], p_range[1], t_range[0], t_range[1]))
    if command is 'price':
        print("Sorting on price:")
        sorted_list = sorted(articles, key = lambda article: article['price'])
    if command is 'latest':
        print("Sorting on date:")
        sorted_list = sorted(articles, key = lambda article: article['time'])

    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    for article in sorted_list:
        try:
            if article['price'] <= p_range[1] and article['price'] >= p_range[0]:
                if article['time'] <= t_range[1] and article['time'] >= t_range[0]:
                    print_info(article)

        except Exception as exc:
            print("Notification: %s" %(exc))
            print("Could not display results from {}".format(article['url']))

def print_info(article):
    print("\n{}".format(article['title']))
    print("\tPrice = {} SEK".format(article['price']))
    print("\t{} Days since the article was posted".format(article['time']))
    print("\tLocation: {}".format(article['place']))
    print("\t{}".format(article['url']))


def load_latest(url):
    directory = "./" + url.split('/')[-1]
    os.chdir(directory)
    list_of_files = glob.glob('*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, "r") as read_file:
            data = json.load(read_file)
    return data


#update("https://www.facebook.com/groups/330486193693264/forsaleposts/?story_id=2097041673704365")


sortby = 'price'
pricerange = [0, 8000]
timerange = [0, 14]

run("https://www.facebook.com/groups/330486193693264/forsaleposts/?story_id=2097041673704365", sortby, pricerange, timerange)

