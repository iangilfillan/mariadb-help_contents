#module imports
import re
from datetime import date

from dataclasses import dataclass
from os.path import join as osjoin

#local imports
from lib.page import format_to_text

DEBUG: bool = True
#lines need to start with this string in order to have it's description read

#classes
@dataclass
class HelpTopic:
    """Basic container for help_topic information"""
    help_topic_id: str
    help_category_id: str
    name: str
    description: str
    example: str
    url: str

#functions
def get_name(url) -> str:
    """returns the unique text in a url eg: mariadb.com/kb/en/insert/ -> insert"""
    #reversing string
    lru = "".join(reversed(url))
    #finding first text inside slashes from top
    eman = re.match(r"/[\w-]+/", lru)[0].strip("/")
    #reversing name back to original order
    name = "".join(reversed(eman))

    return name

def get_help_topic_info(line: str) -> HelpTopic:
    """Returns a HelpTopic containing all the necessary information"""
    pattern = r"insert into help_topic "
    pattern += r"\(help_topic_id,help_category_id,name,description,example,url\) values "
    pattern += r"\((\d+),(\d+),'(.*)','(.*)','()','(.*)'\)"

    return HelpTopic(*re.search(pattern, line).groups())

#main two functions
def read_table_information(read_from: str) -> list:
    """Returns a list containing the HelpTopic from each replacable line"""
    #get lines
    with open(read_from, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    #line needs to start with this to have it's string updated
    insert_into = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values ("
    #get help topic for each line that starts with the required string
    gen = (get_help_topic_info(line) for line in lines if line.startswith(insert_into))
    table_information = [help_topic for help_topic in gen if help_topic.url != ""]

    return table_information, "".join(lines)

def get_new_description(name: str) -> str:
    """Returns new description documentation for the given page name"""
    #if regenerate text bool or if txt file is not in the fetched_pages directory
    with open(osjoin("fetched_html", name + ".html"), "r", encoding="utf-8") as infile:
        html = infile.read()
    new_description = format_to_text(html, name)
    #returns the new description with it's newlines escaped
    return new_description.replace("\n", "\\n")

def update_table_information(content: str, table_information: list) -> str:
    """Updates the new description documentation for each HelpTopic"""
    num_files = len(table_information)

    for index, help_topic in enumerate(table_information):
        #set new information
        name = get_name(help_topic.url)
        new_description = get_new_description(name)
        content = content.replace(help_topic.description, new_description)
        #debug progress
        if DEBUG: print(f"\rRan Through {index+1}/{num_files} files", end="")

    #replace old library url with new url
    content = content.replace("mariadb.com/kb/en/library/", "mariadb.com/kb/en/")
    #update HELP DATE's date
    content = update_help_date(content)
    #removes lines that start with 'update help'
    content = "\n".join([line for line in content.split("\n") if not line.startswith("update help")])

    #new line for prints after this function    
    if DEBUG: print()
    return content

def update_help_date(text: str) -> str:
    """Updates the help date to the current date"""
    #get old description
    for line in text.split("\n"):
        if line.count(",'HELP_DATE',") > 0:
            help_topic = get_help_topic_info(line)
            description = help_topic.description
            break
    #make new description
    today = date.strftime(date.today(),"%d %B %Y")
    #string inputed for HELP_DATE
    updated_description = f"Help contents generated from the MariaDB Knowledge Base on {today}."
    #replace old with new
    text = text.replace(description, updated_description)

    return text

#main imported function
def update_help_table(table_from: str, table_to: str):
    """Reads 'table_from' and updates it's descriptions, writes this to 'table_to'"""
    table_information, content = read_table_information(table_from)
    content = update_table_information(content, table_information)
    with open(table_to, "w", encoding="utf-8") as outfile: outfile.write(content)