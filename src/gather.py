#module imports
import os
import re
import requests

from os.path import join as osjoin
#local imports
from page import Page
from waiter import Waiter
#waiter for request delays
waiter = Waiter(True)

#functions
def fetch_page(url) -> Page:
    """Returns a Page object containing the relevant info and text"""
    name = get_name(url)    

    page_info = get_page_info(name, url)
    page = Page(name, page_info)
    page.format_text()

    return page

def get_page_info(name, url, overwrite=False) -> str:
    """Manages access to the html from the given url, returns the html"""
    existing_pages = os.listdir("fetched_pages")
    filename = name + ".html"
    filepath = osjoin("fetched_pages", filename)

    if not overwrite and filename in existing_pages:
        infile = open(filepath, "r", encoding="utf-8")
        content = infile.read()
        infile.close()
    else:
        content = request_page(url)
        outfile = open(filepath, "w", encoding="utf-8")
        outfile.write(content)
        outfile.close()
    
    return content

def request_page(url) -> str:
    waiter.wait()
    content = requests.get(url).text
    
    return content

def get_name(url) -> str:
    """returns the last text in a url eg: mariadb.com/kb/en/insert/ -> insert"""
    #reversing string
    lru = ""
    for char in url: lru = char + lru
    #finding first text inside slashes from top
    eman = re.match(r"/[\w-]+/", lru)[0].strip("/")
    #reversing name back to original order
    name = ""
    for char in eman.strip("/"): name = char + name
    
    return name

def main() -> None:
    """goes through all files in the csv and requests them"""
    list_of_urls = []
    overwrite = True
    for url in list_of_urls:
        name = get_name(url)
        page_info = get_page_info(name, url, overwrite)

    return None

if __name__ == "__main__":
    main()