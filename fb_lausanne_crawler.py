import requests
import re

def crawl_web(initial_url):
    r = requests.get(initial_url)
    f = open('lausanne.html', 'wb+')
    f.write(r.content)
    f.close()

crawl_web('https://www.facebook.com/groups/330486193693264/')
