#module imports
import os
import re
import requests

from os.path import join as osjoin
#local imports
from page import Page


def fetch_page(url) -> Page:
    name = get_name(url)               

    page_info = get_page_info(name, url)
    page = Page(name, page_info)
    page.format_text()

    return page

def get_page_info(name, url) -> str:
    existing_pages = os.listdir("fetched_pages")
    filename = name + ".html"
    filepath = osjoin("fetched_pages", filename)

    if filename in existing_pages:
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

    content = requests.get(url).text
    
    return content

def get_name(url) -> str:
    lru = ""
    for c in url:
        lru = c + lru

    name = re.match(r"/[\w-]+/", lru)[0]
    output = ""
    for c in name[1:]:
        output = c + output

    return output[1:]
