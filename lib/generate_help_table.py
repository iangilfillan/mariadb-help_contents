import os
import csv
import re
import datetime
import time
import requests
import html as HTML # changing name as gross hack because I used 'html' as a variable name a lot.

from lib.format_to_text import format_to_text
from lib.colors import CL_RED, CL_YELLOW, CL_GREEN, CL_BLUE, CL_END

# custom types
CsvInfo = list[dict[str, str]]
TableInfo = tuple[list[str], list[str], list[str]]

html_files = set(os.listdir("fetched_html"))

#path seperator
SEP = os.sep

def get_help_topic_text(help_topic_id, help_category, name, description, example, url) -> str:
    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values "
    string += f"({help_topic_id},{help_category},'{name}','{description}','{example}','{url}');"
    return string

def get_name(url: str) -> str:
    url = url.removesuffix("/")
    index = url.rindex("/")
    return url[index+1:]

def read_html(name: str) -> str:
    filename = f"{name}.html"
    filepath = f"fetched_html{SEP}{name}.html"
    if filename not in html_files:
        print(f"\nrequesting {name}")
        time.sleep(2)
        html = requests.get(f"https://mariadb.com/kb/en/{name}/").text
        with open(filepath, "w", encoding="utf-8") as outfile:
            outfile.write(str(html))
    else:
        with open(filepath, "r", encoding="utf-8") as infile:
            html = infile.read()

    return html

def write_table_information(table_information: TableInfo, pre_topic_text: str, table_to: str):
    topics, help_keywords, help_relations = table_information

    string_topics: str = "\n".join(topics) + "\n"
    string_help_keywords: str = "\n".join(help_keywords) + "\n"
    string_help_relations: str = "\n".join(help_relations) + "\n"

    with open(table_to, "w", encoding="utf-8") as outfile:
        outfile.write(pre_topic_text)
        outfile.write(string_topics)
        outfile.write(string_help_keywords)
        outfile.write(string_help_relations)
        outfile.write("unlock tables;")

def is_valid_row(row: dict[str, str], urls: set[str], version: int) -> bool:
    
    if row["HELP Include"] == "" or row["HELP Include"] == "0":
        return False
    if version == 1 or row["HELP Include"] == '1':
        pass
    elif (int(row["HELP Include"]) > version):
        return False
    

    url = row["URL"]
    if url in urls:
        print(f"{CL_YELLOW}Duplicate url: '{url}'{CL_END}")
        return False

    urls.add(url)
    return True

def read_csv_information(version: int) -> CsvInfo:
    
    with open(f"input{SEP}kb_urls.csv", "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        urls: set[str] = set()

        rows = [{
                "url": row["URL"],
                "category": row["HELP Cat"],
                "keywords": row["HELP Keywords"],
                } for row in reader if is_valid_row(row, urls, version)]
    return rows

def generate_categories(version: int):
    valid_version = lambda row: int(row["Include"]) <= version or version == 1
    with open(f"input{SEP}help_cats.csv", "r", encoding="utf-8") as infile:
        reader = list(filter(valid_version, csv.DictReader(infile)))
    category_ids: dict[str, int] = {}
    categories: set[str] = set()

    for cat_id, row in enumerate(reader, 1):
        name = row["Name"]
        category_ids[name] = cat_id
        categories.add(name)
    
    output: list[str] = []

    text = "insert into help_category (help_category_id,name,parent_category_id,url)"
    text += " values ({cat_id},'{name}',{parent},'');\n"

    for cat_id, row in enumerate(reader, 1):
        parent = row["Parent"]
        if parent in categories:
            parent = category_ids[parent]
        elif parent != '0':
            print(f"{CL_RED}error for help_cats.csv{parent}{CL_END}")
            continue
        output.append( (text.format(cat_id=cat_id, name=row["Name"], parent=parent)) )
    
    return output

def get_pre_topic_text(version: int) -> str:
    with open(f"input{SEP}starting_sql.sql", "r", encoding="utf-8") as infile:
        start = infile.read()
    
    categories = generate_categories(version)

    return start + "\n" + "".join(categories) + "\n"

def link_help_categories(csv_information: CsvInfo, pre_topic_text: str):
    pattern = r"values \((\d+),'([\w\- ]+)',"

    category_ids: dict[str, int] = {
        category: int(cat_id) for cat_id, category in [
            re.search(pattern, line).groups()
            for line in pre_topic_text.splitlines()
            if line.startswith("insert into help_category")
        ]
    }
    # keys
    help_categories = category_ids.keys()

    for row in list(csv_information):
        if row["category"] in help_categories:
            row["category"] = str(category_ids[row["category"]])
        elif row["category"] != '0':
            name = get_name(row["url"])
            print(f"{CL_YELLOW}{name}: '{row['category']}' was not found in categories{CL_END}")
            csv_information.remove(row)

    csv_information.sort(key=lambda row: int(row["category"]))

def get_page_h1(html):
    index = html.find("<title>")
    end_index = html.find("</title>", index+1)

    title: str = html[index:end_index]
    title: str = title.removeprefix("<title>")
    title: str = title.removesuffix(" - MariaDB Knowledge Base")

    # Converts markers like '&amp'; to their text representations: '&'
    # This is not necessary when getting text from the beautifulsoup structure as it converts automatically.
    title: str = HTML.unescape(title)
    

    return title

def make_table_information(csv_information: CsvInfo) -> tuple[list[str], list[str], list[str]]:

    #list of 'include help topic' lines for the sql table
    topics: list[str] = []
    #list of topics_ids and their extra keywords
    topic_to_keyword: list[tuple[int, str]] = []
    #list of unique keywords
    unique_keywords : list[str] = []

    num_rows: int = len(csv_information)
    # Starting at 2 to make room for HELP DATE
    for help_topic_id, row in enumerate(csv_information, 2):

        name: str = get_name(row["url"])
        html = read_html(name)
        page_name: str = get_page_h1(html)

        keywords: list[str] = row["keywords"].split(";")

        for keyword in keywords:
            if keyword == "": continue
            
            #if is duplicate: warn and skip keyword.
            if keyword.upper() == page_name.upper():
                print(f"\n{CL_YELLOW}Duplicate keyword found: {keyword}{CL_END}")
                continue

            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
            topic_to_keyword.append((help_topic_id, keyword))

        #get topic description
        help_category: str = row["category"]
        description: str = format_to_text(html, name).replace("\n", "\\n")
        #
        topic = get_help_topic_text(help_topic_id, help_category, page_name, description, "", row["url"])

        topics.append(topic)
        # Debug
        row_num: int = help_topic_id
        percent = int((row_num / num_rows) * 100)
        #print differently if processing or finished
        if row_num <= num_rows:
            print(f"\rProgess: {percent}%", end="")
        else:
            print(f"{CL_GREEN}\rFinished: {percent}%{CL_END}")
            time.sleep(0.5)
    #create a dictionary giving each keyword an id
    keyword_ids: dict[str, int] = {keyword: keyword_id for (keyword_id, keyword) in enumerate(unique_keywords, 1)}
    #list where each string is a 'insert help_keyword' line for the sql table
    help_keywords: list[str] = [insert_help_keyword(keyword_id, keyword) for (keyword, keyword_id) in keyword_ids.items()]
    #list where each string is a 'insert help_relations' line for the sql table
    help_relations: list[str] = [insert_help_relations(topic_id, keyword_ids[keyword]) for (topic_id, keyword) in topic_to_keyword]

    topics.insert(0, get_help_date())

    return (topics, help_keywords, help_relations)

def get_help_date() -> str:
    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) "
    string += "values (1,9,'HELP_DATE','Help Contents generated from the MariaDB Knowledge Base on"
    
    today = datetime.date.strftime(datetime.date.today(), "%d %B %Y")
    string += f" {today}.','','');"
    return string

def insert_help_keyword(keyword_id: int, keyword: str) -> str:
    return f"insert into help_keyword values ({keyword_id}, '{keyword}');"

def insert_help_relations(topic_id: int, keyword_id: int) -> str:
    return f"insert into help_relation values ({topic_id}, {keyword_id});"

#main import function
def generate_help_table(table_to: str, version: int):
    pre_topic_text: str = get_pre_topic_text(version)
    csv_information = read_csv_information(version)
    link_help_categories(csv_information, pre_topic_text)
    table_information = make_table_information(csv_information)

    write_table_information(table_information, pre_topic_text, table_to)
