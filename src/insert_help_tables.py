#module imports
import re
import time
import sys
import os

from dataclasses import dataclass
from os.path import join as osjoin

#local imports
from page import Page
#config

REGENERATE_TEXT = False
DEBUG = True
#consts
FETCHED_PAGES = os.listdir("fetched_pages")
INSERT_INTO = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values ("


#classes
@dataclass
class HelpTopic:
    help_topic_id: str
    help_category_id: str
    name: str
    description: str
    example: str
    url: str

#functions

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

def get_help_topic_info(line) -> HelpTopic:
    """Creates a """
    pattern = r"insert into help_topic \(help_topic_id,help_category_id,name,description,example,url\) values "
    pattern += r"\((\d+),(\d+),'(.*)','(.*)','()','(.*)'\)"

    return HelpTopic( *re.search(pattern, line).groups() )

def read_table_information(read_from) -> list:
    """Returns a list containing the HelpTopic from each replacable line"""
    table_information = []
    #get lines
    with open(read_from, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    #get help topics
    gen = (get_help_topic_info(line) for line in lines if line.startswith(INSERT_INTO))
    table_information = [help_topic for help_topic in gen if help_topic.url != ""]

    return table_information



def update_table_information(table_information) -> None:

    num_files = len(table_information)
    for index, help_topic in enumerate(table_information):
        #debug
        if DEBUG:
            sys.stdout.write(f"\rRan Through {index+1}/{num_files} files")
            sys.stdout.flush()
        #set new information
        name = get_name(help_topic.url)
        help_topic.new_description = get_new_description(name)
    
    return None

def get_new_description(name):

    if REGENERATE_TEXT or name+".txt" not in FETCHED_PAGES:
        #read, convert, set new description
        with open(osjoin("fetched_pages", name+".html"), "r", encoding="utf-8") as infile:
            page = Page(name, infile.read())
            page.format_text()
            new_description = page.text
    else:
        #read and set
        with open(osjoin("fetched_pages", name+".txt"), "r", encoding="utf-8") as infile:
            new_description = infile.read().replace("\n", "\\n")
    
    return new_description

def insert_into_help_table(fp, table_information) -> None:
    #read help table
    with open(fp, "r", encoding="utf-8") as infile:
        text = infile.read()
    #For each help table, replace the old description with the new description
    for help_topic in table_information:
        #replace old description
        text = text.replace(help_topic.description, help_topic.new_description)
        #replace old url
        url = help_topic.url.replace("/library", "")
        text = text.replace(help_topic.url, url)
    with open(fp, "w", encoding="utf-8") as outfile:
        outfile.write(text)

    return None

def main():
    #Create the directory 'current_text_files' if absent
    if "current_text_files" not in os.listdir(): os.makedirs("current_text_files")
    #get fill_help_tables.sql info
    table_information = read_table_information("fill_help_tables.sql")
    #copy fill_help_tables
    with open("fill_help_tables.sql", "r", encoding="utf-8") as infile: content = infile.read()
    with open("new_help_tables.sql", "w", encoding="utf-8") as outfile: outfile.write(content)
    #update table_information
    update_table_information(table_information)
    insert_into_help_table("new_help_tables.sql", table_information)

    return None

if __name__ == "__main__":
    main()