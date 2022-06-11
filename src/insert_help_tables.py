#module imports
import re
import time
import sys
import os

from dataclasses import dataclass


from os.path import join as osjoin
#local imports
from gather import get_name, fetch_page
@dataclass
class HelpTopic:
    help_topic_id: str
    help_category_id: str
    name: str
    description: str
    example: str
    url: str

#functions
def get_help_topic_info(line) -> HelpTopic:
    pattern = r"insert into help_topic \(help_topic_id,help_category_id,name,description,example,url\) values "
    pattern += r"\((\d+),(\d+),'(.*)','(.*)','()','(.*)'\)"

    help_topic_id, help_category_id, name, description, example, url = re.search(pattern, line).groups()

    return HelpTopic(help_topic_id, help_category_id, name, description, example, url)

def is_help_topic(line) -> bool:

    output = line.startswith(
        "insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values ("
        )

    return output

def read_table_information(read_from, write_text_files=True) -> list:
    table_information = []
    #get lines
    infile = open(read_from, "r", encoding="utf-8")
    lines = infile.readlines()
    infile.close()

    for line in lines:
        
        if is_help_topic(line):
            #seperate information
            help_topic = get_help_topic_info(line)
            #update old urls
            if help_topic.url == "": continue
            help_topic.url = help_topic.url.replace("/library", "")
            #store information
            table_information.append(help_topic
            )

            if write_text_files:
                #create readable description with newlines
                readable_description = help_topic.description.replace("\\n", "\n")
                #get file name and path
                help_topic.id_name = get_name(help_topic.url)
                fpath = osjoin("current_text_files", help_topic.id_name+".txt")
                #write description
                outfile = open(fpath, "w", encoding="utf-8")
                outfile.write(readable_description)
                outfile.close()
    
    return table_information

def update_table_information(table_information, regenerate_text) -> None:
    forced_line_splits = 0
    start_time = time.perf_counter()

    num_files = len(table_information)
    for index, help_topic in enumerate(table_information):
        #debug
        sys.stdout.write(f"\rRan Through {index+1}/{num_files} files")
        sys.stdout.flush()
        #set new information
        if regenerate_text:
            page = fetch_page(help_topic.url)
            help_topic.new_description = page.text
            forced_line_splits += page.forced_line_splits
        else:
            filename = get_name(help_topic.url) + ".txt"
            infile =  open(osjoin("fetched_pages", filename), encoding="utf-8")
            new_desc = infile.read()
            infile.close()
            help_topic.new_description = new_desc.replace("\n", "\\n")

    time_taken = time.perf_counter() - start_time

    print("\n")
    if forced_line_splits > 0: print(f"{forced_line_splits} - TOTAL FORCED LINE SPLITS - {forced_line_splits}")
    print(f"Took {round(time_taken, 2)}s to run {num_files} files")
    print(f"Avg of {round(time_taken / num_files, 3)}s per file")

    return None

def insert_into_help_table(fp, table_information) -> None:
    
    #read help table
    infile = open(fp, "r", encoding="utf-8")
    help_table = infile.read()
    infile.close()
    #replace

    for help_topic in table_information:
        help_table = help_table.replace(help_topic.description, help_topic.new_description.replace("\n", "\\n"))

    outfile = open(fp, "w", encoding="utf-8")
    outfile.write(help_table)
    outfile.close()

    return None

def main():
    if "current_text_files" not in os.listdir(): os.makedirs("current_text_files")
    regenerate_text = False
    #get fill_help_tables.sql info
    table_information = read_table_information("fill_help_tables.sql", False)
    #copy fill_help_tables
    with open("fill_help_tables.sql", "r", encoding="utf-8") as infile: content = infile.read()
    with open("new_help_tables.sql", "w", encoding="utf-8") as outfile: outfile.write(content)
    #update table_information
    update_table_information(table_information, regenerate_text)
    insert_into_help_table("new_help_tables.sql", table_information)

    return None

if __name__ == "__main__":
    main()