import os
import csv
import datetime
import requests

from html import unescape # Gross hack because I used 'html' as a variable name a lot.

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

def read_html(name: str, url: str) -> str:
    filename = f"{name}.html"
    filepath = f"fetched_html{SEP}{name}.html"
    if filename not in html_files:
        print(f"\n{CL_BLUE}requesting {name}{CL_END}")
        req = requests.get(url)
        status = req.status_code
        test_status_codes(status, url)
        html = req.text
        with open(filepath, "w", encoding="utf-8") as outfile:
            outfile.write(str(html))
    else:
        with open(filepath, "r", encoding="utf-8") as infile:
            html = infile.read()

    return html

def test_status_codes(status_code: int, url: str):
    invalid_codes = [404]
    if status_code in invalid_codes:
        print(f"{CL_RED}Invalid url {url}{CL_END}")
        exit(1)
    
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

def read_csv_information(version: int) -> CsvInfo:
    with open(f"input{SEP}kb_urls.csv", 'r', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        urls: set[str] = set() # Used for is_valid_row
        desired_length: int = len(reader.fieldnames)
        rows = [{
                "url": row["URL"],
                "category": row["HELP Cat"],
                "keywords": row["HELP Keywords"],
                } for row in reader if is_valid_row(row, urls, version, desired_length)
        ]
    return rows

def is_valid_row(row: dict[str, str], urls: set[str], version: int, desired_length: int) -> bool:
    if len(row) != desired_length:
        print(f"{CL_RED}Invalid row length: {row['URL']}{CL_END}")
        exit(1)

    if row["HELP Include"] == '' or row["HELP Include"] == '0':
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

def generate_categories(version: int):
    is_valid_version = lambda row: int(row["Include"]) <= version or version == 1
    
    infile = open(f"input{SEP}help_cats.csv", 'r', encoding="utf-8")
    csv_rows = list(filter(is_valid_version, csv.DictReader(infile)))
    infile.close()
    # Give each category an id
    category_ids: dict[str, int] = {
        row["Name"]: cat_id
        for (cat_id, row) in enumerate(csv_rows, 1)
    }
    # Add '0' as it does not exist in the csv
    category_ids['0'] = 0

    # SQL format
    text = "insert into help_category (help_category_id,name,parent_category_id,url)" \
           " values ({cat_id},'{name}',{parent},'');\n"
    # Format each line
    category_strings: list[str] = [
        (text.format(cat_id=cat_id, name=row["Name"], parent=category_ids[row["Parent"]]))
        if row["Parent"] in category_ids or row["Parent"] == '0'
        else (print(f"{CL_RED}Error for help_cats.csv ({row['Parent']}){CL_END}"), exit()) # Maybe I should just use a for loop...
        for cat_id, row in enumerate(csv_rows, 1)
    ]
    return category_strings, category_ids

def get_pre_topic_text(version: int) -> tuple[str, dict[str, int]]:
    infile = open(f"input{SEP}starting_sql.sql", 'r', encoding="utf-8")
    file_sql = infile.read()
    infile.close()

    categories, category_info = generate_categories(version)
    pre_topic_text: str = file_sql + "\n" + "".join(categories) + "\n"

    return pre_topic_text, category_info

def link_help_categories(csv_information: CsvInfo, category_ids):

    for row in list(csv_information):
        if row["category"] in category_ids:
            row["category"] = str(category_ids[row["category"]])
        else:
            name = get_name(row["url"])
            print(f"{CL_YELLOW}{name}: '{row['category']}' was not found in categories{CL_END}")
            csv_information.remove(row)

    csv_information.sort(key=lambda row: int(row["category"]))

def get_page_h1(html: str, name: str):
    if not ("<title>" in html and "</title>" in html):
        print(f"\n{CL_RED}Did not find title tag in '{name}'")
        exit()

    index = html.index("<title>")
    end_index = html.index("</title>", index+1)

    title: str = html[index:end_index]\
        .removeprefix("<title>")\
        .removesuffix(" - MariaDB Knowledge Base")
    # Converts html escape sequences like '&amp'; to their text representations: '&'
    return unescape(title)

def make_table_information(csv_information: CsvInfo) -> tuple[list[str], list[str], list[str]]:
    topics: list[str] = []
    topic_to_keyword: list[tuple[int, str]] = []
    unique_keywords : list[str] = []

    num_rows: int = len(csv_information)
    # Starting at 2 to make room for HELP DATE
    for help_topic_id, row in enumerate(csv_information, 2):
        name: str = get_name(row["url"])
        html = read_html(name, row["url"])
        page_name: str = get_page_h1(html, name)

        keywords: list[str] = row["keywords"].split(";")
        # If keywords remains singular this for loop will be removed
        for keyword in keywords:
            if keyword == "": continue
            # if is duplicate: warn and skip keyword.
            if keyword.upper() == page_name.upper():
                print(f"\n{CL_YELLOW}Duplicate keyword found: {keyword}{CL_END}")
                continue

            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
            topic_to_keyword.append((help_topic_id, keyword))

        description: str = format_to_text(html, name).replace("\n", "\\n")

        topics.append(get_help_topic_text(
            help_topic_id, row["category"], page_name,
            description, "", row["url"])
        )

        row_num: int = help_topic_id
        percent = int((row_num / num_rows) * 100)

        if row_num <= num_rows:
            print(f"\rProgess: {percent}%", end="")
        else:
            print(f"{CL_GREEN}\rFinished: {percent}%{CL_END}")

    keyword_ids: dict[str, int] = {
        keyword: keyword_id for (keyword_id, keyword)
        in enumerate(unique_keywords, 1)
    }
    help_keywords: list[str] = [
        insert_help_keyword(keyword_id, keyword)
        for (keyword, keyword_id) in keyword_ids.items()
    ]
    help_relations: list[str] = [
        insert_help_relations(topic_id, keyword_ids[keyword])
        for (topic_id, keyword) in topic_to_keyword
    ]
    topics.insert(0, get_help_date())

    return (topics, help_keywords, help_relations)

def get_help_date() -> str:
    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) "
    string += "values (1,9,'HELP_DATE','Help Contents generated from the MariaDB Knowledge Base on "
    
    today = datetime.date.strftime(datetime.date.today(), "%d %B %Y")
    string += f"{today}.','','');"
    return string

def insert_help_keyword(keyword_id: int, keyword: str) -> str:
    return f"insert into help_keyword values ({keyword_id}, '{keyword}');"

def insert_help_relations(topic_id: int, keyword_id: int) -> str:
    return f"insert into help_relation values ({topic_id}, {keyword_id});"

#main import function
def generate_help_table(table_to: str, version: int):
    pre_topic_text, category_info = get_pre_topic_text(version)
    csv_information = read_csv_information(version)
    link_help_categories(csv_information, category_info)
    table_information = make_table_information(csv_information)

    write_table_information(table_information, pre_topic_text, table_to)