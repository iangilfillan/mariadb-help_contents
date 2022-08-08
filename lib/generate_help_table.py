import os
import csv
import re
import datetime

from lib.format_to_text import format_to_text

# custom types
CsvInfo = list[dict[str, str]]

TableInfo = tuple[list[str], list[str], list[str]]

#path seperator
SEP = os.sep

def get_help_topic_text(help_topic_id, help_category, name, description, example, url) -> str:
    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values "
    string += f"({help_topic_id},{help_category},'{name}','{description}','{example}','{url}');"
    return string

def is_valid_row(row: dict, urls: set[str]) -> bool:
    if row["HELP Include"] != "1":
        return False
    
    if row["URL"] in urls:
        print(row["URL"])
        return False

    urls.add(row["URL"])
    return True

def get_name(url: str) -> str:
    url = url.removesuffix("/")
    index = url.rfind("/")
    return url[index+1:]

def read_html(name: str) -> str:
    filepath = f"fetched_html{SEP}{name}.html"

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

def generate_categories():
    with open(f"input{SEP}help_cats.csv", "r", encoding="utf-8") as infile:
        reader = list(csv.DictReader(infile))
    
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
            print("error for help_cats.csv", parent)
            continue
        output.append( (text.format(cat_id=cat_id, name=row["Name"], parent=parent)) )
    
    return output

def get_pre_topic_text() -> str:
    with open(f"input{SEP}starting_sql.sql", "r", encoding="utf-8") as infile:
        start = infile.read()
    
    categories = generate_categories()

    return start + "\n" + "".join(categories) + "\n"

def read_csv_information() -> CsvInfo:
    with open(f"input{SEP}kb_urls.csv", "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        urls: set[str] = set()

        rows = [{
                "url": row["URL"],
                "category": row["HELP Cat"],
                "keywords": row["HELP Keywords"],
                } for row in reader if is_valid_row(row, urls)]

    return rows

def link_help_categories(csv_information: CsvInfo, pre_topic_text: str):

    category_ids: dict[str, int] = {}

    pattern = r"values \((\d+),'([\w\- ]+)',"

    for line in pre_topic_text.split("\n"):
        if line.startswith("insert into help_category"):
            match = re.search(pattern, line)
            if match is None: continue
            help_category_id, help_category = match.groups()
            category_ids[help_category] = int(help_category_id)

    # keys
    help_categories = set(category_ids)
    for row in list(csv_information):
        if row["category"] in help_categories:
            row["category"] = str(category_ids[row["category"]])
        elif row["category"] != '0':
            name = get_name(row["url"])
            print(f"{name}: '{row['category']}' was not found in categories")
            csv_information.remove(row)

    csv_information.sort(key=lambda row: int(row["category"]))

def get_page_h1(html):
    index = html.find("<title>")
    end_index = html.find("</title>", index+1)

    title: str = html[index:end_index]
    title = title.removeprefix("<title>")
    title = title.removesuffix(" - MariaDB Knowledge Base")

    return title

def make_table_information(csv_information: CsvInfo) -> tuple[list[str], list[str], list[str]]:

    #list of 'include help topic' lines for the sql table
    topics: list[str] = []
    #list of topics_ids and their extra keywords
    topic_to_keyword: list[tuple[int, str]] = []
    #list of unique keywords
    unique_keywords : list[str] = []

    for help_topic_id, row in enumerate(csv_information, 1):
        keywords: list[str] = row["keywords"].split(";")
        topic = row["url"]

        for keyword in keywords:
            if keyword == "": continue
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
            topic_to_keyword.append((help_topic_id, keyword))

        name: str = get_name(topic)
        #get topic description
        help_category: str = row["category"]
        html = read_html(name)
        page_name: str = get_page_h1(html)
        description: str = format_to_text(html, name).replace("\n", "\\n")

        topic = get_help_topic_text(help_topic_id, help_category, page_name, description, "", row["url"])

        topics.append(topic)

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
def generate_help_table(table_to: str):
    pre_topic_text: str = get_pre_topic_text()
    csv_information = read_csv_information()
    link_help_categories(csv_information, pre_topic_text)
    table_information = make_table_information(csv_information)

    write_table_information(table_information, pre_topic_text, table_to)
