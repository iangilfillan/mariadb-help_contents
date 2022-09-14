import csv
import datetime
import requests

from html import unescape
from pathlib import Path

from lib.format_to_text import format_to_text
import lib.debug as debug
# custom types
CsvInfo = list[dict[str, str]]
TableInfo = tuple[list[str], list[str], list[str]]

#path seperator
def get_help_topic_text(help_topic_id, help_category, name, description: str, example, url) -> str:
    unaltered = description

    high = 14000
    low = 13000
    parts = []
    while len(description) >= high:
        index = description.find("\\n", max(low, len(description)-low))
        if index == -1:
            debug.warn(f"Could not fine newline for help_topic concat {name}")
            index = low
        parts.append(description[:index])
        description = description[index:]
    
    parts.append(description)
    description = parts.pop(0)

    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values "
    string += f"({help_topic_id},{help_category},'{name}','{description}','{example}','{url}');"

    rejoin = description
    for text in parts:
        if len(text) >= high:
            print()
            debug.warn(f"help_topic concat has length: {len(text)}")
        string += add_update_help_topic(text, help_topic_id)
        rejoin += text
    
    if rejoin != unaltered:
        print()
        debug.error(f"Did not seperate description correctly for {name}")
    return string

def add_update_help_topic(text: str, help_topic_id: int) -> str:
    return f"\nupdate help_topic set description = CONCAT(description, '{text}') WHERE help_topic_id = {help_topic_id};"

def get_name(url: str) -> str:
    url = url.removesuffix("/")
    index = url.rindex("/")
    return url[index+1:]

def read_html(name: str, url: str) -> str:
    filepath = Path(f"fetched_html/{name}.html")
    if not filepath.exists():
        print()
        debug.info(f"Requesting {name}")
        req = requests.get(url)
        html = req.text
        test_status_codes(req.status_code, url)
        filepath.write_text(str(html), encoding="utf-8")
    else:
        html = filepath.read_text(encoding="utf-8")
    
    return html

def test_status_codes(status_code: int, url: str):
    invalid_codes = [404]
    if status_code in invalid_codes:
        debug.error(f"Invalid url {url}")

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
        outfile.write("unlock tables;\n")

def read_csv_information(version: int) -> CsvInfo:
    with open(Path("input/kb_urls.csv"), 'r', encoding="utf-8") as infile:
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
        debug.error(f"Invalid row length: " + row["URL"])

    if row["URL"] != "" and row["HELP Include"] == "":
        debug.warn("No Help Include for " + row["URL"])

    if row["HELP Include"] in ["", '0']:
        return False
    if version == 1 or row["HELP Include"] == '1':
        pass
    elif (int(row["HELP Include"]) > version):
        return False
    
    url = row["URL"]
    if url in urls:
        debug.warn(f"Duplicate url: '{url}'")
        return False

    urls.add(url)
    return True

def generate_categories(version: int):
    def is_valid_version(row: dict[str, str]):
        if not row["Include"].isnumeric():
            debug.error(f"Include must be a number: {row['Name']}")
        return int(row["Include"]) <= version or version == 1
    
    infile = Path("input/help_cats.csv").read_text(encoding="utf-8")
    unfiltered = csv.DictReader(infile.splitlines())
    
    csv_rows = list(filter(is_valid_version, unfiltered))
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
        else debug.error(f"Issue for help_cats.csv ({row['Parent']})")
        for cat_id, row in enumerate(csv_rows, 1)
    ]
    return category_strings, category_ids

def get_pre_topic_text(version: int) -> tuple[str, dict[str, int]]:
    file_sql = Path("input/starting_sql.sql").read_text(encoding="utf-8")

    categories, category_info = generate_categories(version)
    pre_topic_text: str = file_sql + "\n" + "".join(categories) + "\n"

    return pre_topic_text, category_info

def link_help_categories(csv_information: CsvInfo, category_ids):

    for row in list(csv_information):
        if row["category"] in category_ids:
            row["category"] = str(category_ids[row["category"]])
        else:
            name = get_name(row["url"])
            debug.warn(f"\n{name}: '{row['category']} was not found in categories")
            csv_information.remove(row)

    csv_information.sort(key=lambda row: int(row["category"]))

def get_page_h1(html: str, name: str):
    if not ("<title>" in html and "</title>" in html):
        debug.error(f"Did not find title tag in '{name}'")

    index = html.index("<title>")
    end_index = html.index("</title>", index+1)

    title: str = html[index:end_index]\
        .removeprefix("<title>")\
        .removesuffix(" - MariaDB Knowledge Base")
    # Converts html escape sequences like '&amp'; to their text representations: '&'
    return unescape(title)

def make_table_information(csv_information: CsvInfo, version: int) -> tuple[list[str], list[str], list[str]]:
    topics: list[str] = []
    topic_to_keyword: list[tuple[int, str]] = []
    unique_keywords : list[str] = []

    num_rows: int = len(csv_information)
    try:
        # Starting at 3 to make room for HELP DATE AND HELP_VERSION
        for help_topic_id, row in enumerate(csv_information, 3):
            name: str = get_name(row["url"])
            html = read_html(name, row["url"])
            page_name: str = get_page_h1(html, name)

            keywords: list[str] = row["keywords"].split(";")
            # If keywords remains singular this for loop will be removed
            for keyword in keywords:
                if keyword == "": continue
                # if is duplicate: warn and skip keyword.
                if keyword.upper() == page_name.upper():
                    print()
                    debug.warn(f"Duplicate keyword found: {keyword}")
                    continue

                if keyword not in unique_keywords:
                    unique_keywords.append(keyword)
                topic_to_keyword.append((help_topic_id, keyword))

            description: str = format_to_text(html, name)

            topics.append(get_help_topic_text(
                help_topic_id, row["category"], page_name,
                description, "", row["url"])
            )

            row_num: int = help_topic_id
            percent = int((row_num / num_rows) * 100)

            if row_num < num_rows+2: # to for help_date and help_version (TODO fix hack)
                print(f"\rProgess: {percent}%", end="")
            else:
                print()
                debug.success(f"Finished {percent}%")
    except KeyboardInterrupt:
        print()
        debug.error("Keyboard Interrupt")
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
    topics.insert(1, get_help_version(version))
    
    return (topics, help_keywords, help_relations)

def get_help_date() -> str:
    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) "
    string += "values (1,9,'HELP_DATE','Help Contents generated from the MariaDB Knowledge Base on "
    
    today = datetime.date.strftime(datetime.date.today(), "%d %B %Y")
    string += f"{today}.','','');"
    return string

def get_help_version(version: int) -> str:    
    today = datetime.date.strftime(datetime.date.today(), "%d %B %Y")

    version = str(version)
    version_str = version[:2] + '.' + version[2:]
    text = f"Help Contents generated for MariaDB {version_str} from the MariaDB Knowledge Base on {today}."

    string = "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) "
    string += f"values (2,9,'HELP_VERSION','{text}','','');"

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
    table_information = make_table_information(csv_information, version)

    write_table_information(table_information, pre_topic_text, table_to)