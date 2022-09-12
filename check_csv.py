import csv
import sys
from pathlib import Path

SQL_FILEPATH = Path("output/fill_help_tables.sql")

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
    help_table = SQL_FILEPATH.read_text(encoding="utf-8").splitlines()

    urls = []
    for index, line in enumerate(help_table):
        if not line.endswith("/');\n"): continue
        line = line.replace("/library", "")
        index = line.rfind("https://mariadb.com/kb/en")
        if index == -1: continue
        url = line[index:-4]
        urls.append(url)

    return urls

def get_csv_urls_and_version():
    infile = Path("input/kb_urls.csv").read_text()
    reader = list(csv.DictReader(infile.splitlines()))
    return [(line["URL"], line["HELP Include"]) for line in reader]

def main():
    help_table_urls = get_help_table_urls()
    csv_urls = [url for index, (url, version) in enumerate(get_csv_urls_and_version()) if is_correct_version(url, version, index)]

    not_in_help = [url for url in csv_urls if url not in help_table_urls]
    not_in_csv = [url for url in help_table_urls if url not in csv_urls]

    Path("output/not_in_help.txt").write_text("\n".join(not_in_help))
    Path("output/not_in_csv.txt").write_text("\n".join(not_in_csv))

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please Enter a version number", end="")
    else:
        version: str = sys.argv[1]
        issues: list[str] = []
        main()