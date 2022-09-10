import csv
import sys
from pathlib import Path

SQL_FILENAME = "fill_help_tables.sql"


def is_correct_version(url: str, version: str, line_num: int) -> bool:
    """Tests if the help table version is greater than or equal to the line version"""
    #defaults to zero
    if version == "": version = "0"

    if not version.replace(".", "").isnumeric():
        issues.append(f"{line_num+1} - ({url}): Cannot convert HELP include '{version}' to version number")
        return False

    if version == "0" or float(version) < float(version):
        return False
    if version == "1" or float(version) >= float(version):
        return True

    issues.append(f"{line_num+1} - ({url}): Incorrect version number")
    return False

def get_help_table_urls():
    with open(SQL_FILENAME, "r", encoding="utf-8") as infile:
        help_table = infile.readlines()

    urls = []
    for index, line in enumerate(help_table):
        if not line.endswith("/');\n"): continue
        #update url
        line = line.replace("/library", "")
        #find url
        index = line.rfind("https://mariadb.com/kb/en")
        if index == -1: continue
        url = line[index:-4]
        #print(url)
        urls.append(url)

    return urls

def get_csv_urls_and_version():
    with open(Path("input/kb_urls.csv"), "r") as infile:
        reader = list(csv.DictReader(infile))
    return [(line["URL"], line["HELP Include"]) for line in reader]

def main():
    not_in_help = []
    not_in_csv = []

    help_table_urls = get_help_table_urls()
    csv_urls = []

    for index, (url, version) in enumerate(get_csv_urls_and_version()):
        if is_correct_version(url, version, index):
            csv_urls.append(url)
            if url not in help_table_urls:
                not_in_help.append(url + "\n")
            #else:
                #issues.append(f"{url} was found multiple times")
    for url in help_table_urls:
        #if "select/" in url: print(url)
        if url not in csv_urls:
            not_in_csv.append(url + "\n")

    if len(issues) != 0:
        print("Issues")
        [print(issue) for issue in issues]
    
    with open("not_in_help.txt", "w", encoding="utf-8") as outfile:
        outfile.writelines(not_in_help)
    with open("not_in_csv.txt", "w", encoding="utf-8") as outfile:
        outfile.writelines(not_in_csv)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please Enter a version number", end="")
    else:
        version: str = sys.argv[1]
        issues: list[str] = []
        main()
