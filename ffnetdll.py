#Downloads a link and the content linked to from that page
import os
import bs4
import requests
from requests.compat import urljoin
import re
from bs4 import BeautifulSoup

"""
@funct: Checks if a url can be reached, if so extracts the content and turns it into a BeautifulSoup
@param: an url
@retur: a soup
"""
def create_soup(url):
    print(f"Making soup of {url}")
    response = get_response(url)

    if response.status_code == 200:
        print('Success!')
    elif response.status_code == 404:
        print('Not Found')
        return
    
    #Extract the content
    content = response.content

    #Generate structure for parsing the html
    soup = BeautifulSoup(content, features="html.parser")
    
    return soup

""" 
@funct: Given a soup, extracts the content from a tag with a set id
"""

def consume_story(soup):
    #Extract THE FIRST tag with the correct id storytext; this is the actual chapter
    story = soup.find(id='storytext')
    return story

""" 
@funct: Given a soup, extracts the content from a tag with a set id, then uses regex to find the chapter count
"""

def consume_chapter_count(soup):
    story_meta_info = soup.find(id = "profile_top")
    chapter_count = re.search("(?<=Chapters: )\d+", str(story_meta_info))
    chapter_count = int(chapter_count.group(0))
    return chapter_count

""" 
@funct: Tries to get a response object from a given url, can raise error
"""
def get_response(url):
    try:
        response = requests.get(url)
        return response
    except Exception as exc:
        print(f"Notification: {exc}" )

""" 
@funct: function to join an url together. Just separated from run to remove clutter
@param: the three parts of a ff.net url
@retur: the full url
"""
def make_chapter_url(base, chapter, title):
    chapter_url = urljoin(base, str(chapter) + '/')
    chapter_url = urljoin(chapter_url, title)
    return(chapter_url)
     


""" 
@funct: Main program. Waits for an URL from the user, checks that it's a valid ff.net page, extracts chapter count, extracts the story in html format from each page and joins it together, creating a single html page containing everything.
"""
def run():
    #Setup
    url = input("Please enter the url of the story\n")
    
    try:
        #Get base URL
        base_url = re.search('.*\/(?=1\/)', url).group(0)

        #Get story title
        story_title = re.search('(?<=\/1\/).*', url).group(0)

    except Exception as exc:
        print(f"ERROR\nMalformed url, or ff.net has changed their layout. Soz :/\n{exc}" )
        return

    #Set starting point
    current_chapter = 1

    #Get total chapter count
    chapter_url = make_chapter_url(base_url, current_chapter, story_title)
    soup = create_soup(chapter_url)
    nr_chapters = consume_chapter_count(soup)

    WHOLE_STORY = ""

    for current_chapter in range(1, nr_chapters + 1):
        chapter_url = make_chapter_url(base_url, current_chapter, story_title)
        soup = create_soup(chapter_url)
        story = consume_story(soup)
        WHOLE_STORY +=  str(story)

    f = open(f"{story_title}.html","w+")
    f.write(WHOLE_STORY)
    print("done")






run()
