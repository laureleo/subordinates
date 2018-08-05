import requests
import re
#.*?... match as few as possible until ...
#(?=...) match, but do not return ...
#\Z EOF
# Given a start url, consumes all subpages of that site and stores them on the disk
 
print("Site Sucker: RUNNING")


#Uses a regex to check the robots.txt and returns the URL:s we aren't allowed to crawl.
def check_permissions(current_url):
    user = '\*'
    forbidden_urls = []
    html = requests.get(current_url + '/robots.txt')
    if not html:
        print("Could not retrieve robots.txt")
        return []

    text = str(html.content)

    # Compile the pattern for recognizing the segment relevant for the <user> (cp1) and for extracting the disallowed urls (cp2)
    cp1 = re.compile('user-agent:\s?' + user + '\s?.*?(?=user-agent|\Z)', re.IGNORECASE)
    cp2 = re.compile('disallow:\s?(?P<url>.*)', re.IGNORECASE)

    relevant_part = cp1.search(text)
    if not relevant_part:
        print("Could not find rules for robot named " + user)
        return []

    lines = relevant_part.group().split('\\n')
    for line in lines:
        match = cp2.search(line)
        if match:
            forbidden_urls.append(current_url + match.group('url'))

    return forbidden_urls

#Checks if the url we're about to visit starts with any of the forbidden urls. If forbidden, return True, else false
def forbidden(current_url, forbidden_urls):
    for url in forbidden_urls:
        match = re.search(url, current_url, re.IGNORECASE)
        if match:
            print(match.group())
            return True
    return False

def crawl(initial_url):
    crawled = []
    blocked = []
    to_crawl = []
    to_crawl.append(initial_url)

    disallowed = check_permissions(initial_url)

    while to_crawl:
        #Get the topmost url in the list of urls to visit
        current_url = to_crawl.pop(0)
        print("Crawling " + current_url)

        #Check if visiting this url is disallowed by the robots.txt
        if forbidden(current_url, disallowed):
            blocked.append(current_url)
            print("Tried to check " + current_url + " but lacked permission")
            continue

        #If not disallowed, get the data from the url
        r = requests.get(current_url)
        crawled.append(current_url)

        #Grab all urls, including relative paths
        for url in re.findall('<a href="([^"]+)">', str(r.content)):
            if url[0] == '/':
                url = current_url + url
            #If the url is a subsite, add it to the list of things to crawl.
            pattern = re.compile('https?')
            if pattern.match(url):
                to_crawl.append(url)

    return crawled, blocked, to_crawl

crawl('https://www.splunk.com')
#crawl('https://www.youtube.com/watch?v=KPxSS1zHWwQ&start_radio=1&list=RDMMKPxSS1zHWwQ')
#crawl('https://www.facebook.com')
#crawl('https://www.mangareader.net')
print("TASK COMPLETED")
