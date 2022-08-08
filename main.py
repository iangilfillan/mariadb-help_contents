"""Version selecting and debug info, interface to run generation script"""
import time
import sys, os
from lib.generate_help_table import generate_help_table
from lib.colors import CL_YELLOW, CL_RED, CL_GREEN, CL_BLUE, CL_CYAN, CL_END
# Preparing system for colored text
os.system('')

# OS path seperator
SEP = os.sep

# Paths to output sql file
SQL_FILENAME: str = "new_help_tables.sql"
SQL_FILEPATH: str = f"output{SEP}{SQL_FILENAME}"

# Functions
def get_version() -> int:
    """Reads the version number while giving precise debug info"""
    if len(sys.argv) < 2:
        version = 1
        print(f"{CL_YELLOW}Warning! No version number given, defaults to 0.{CL_END}")
    elif not sys.argv[1].isnumeric():
        print(f"{CL_RED}Invalid version argument!{CL_END}", end="")
        exit()
    elif sys.argv[1] == '0':
        print(f"{CL_RED}Cannot have 0 as version number!{CL_END}", end="")
        exit()
    elif len(sys.argv[1]) not in [3, 4]:
        print(f"{CL_RED}Version number must be of length 3 or 4 (eg. 105, 1010)")
        exit()
    elif sys.argv[1][0] != "1":
        print(f"{CL_RED}Version must start with '1' (eg. 105, 1010)")
        exit()
    elif sys.argv[1][1] != "0":
        print(f"{CL_YELLOW}Warning! Versions above 10.x not accounted for.{CL_END}")
        version = version = int(sys.argv[1])
    elif int(sys.argv[1][2:]) < 3:
        print(f"{CL_YELLOW}Warning! Versions below 10.3 have no effect.{CL_END}")
        version = int(sys.argv[1])
    elif sys.argv[1][2] == '0':
        print(f"{CL_BLUE}Note! Unnecessary '0' for third digit.{CL_END}")
        version = int(sys.argv[1])
    else:
        version = int(sys.argv[1])
        print(f"{CL_GREEN}Selected Version: {version}.{CL_END}")
    
    # Extra newline for style points
    print()
    # Give time to read message
    # time.sleep(0.2)
    return version

def read_new_table() -> str:
    """Reads output SQL file"""
    table = ""
    if SQL_FILENAME in os.listdir("output"):
        with open(SQL_FILEPATH, "r", encoding="utf-8") as sql_file:
            table = sql_file.read()

    return table

def print_change(old_file: str, new_file: str):
    """Checks whether SQL file has been modified"""
    if old_file == "":
        print(f"{CL_BLUE}Wrote to {SQL_FILEPATH}{CL_END}")
    elif old_file != new_file:
        print(f"{CL_BLUE}Updated {SQL_FILENAME}{CL_END}")
    else:
        print(f"{CL_BLUE}No change was made to {SQL_FILEPATH}{CL_END}")

def main():
    #keep track of generated_table
    old_file: str = read_new_table()
    
    #retrive version
    version: int = get_version()
    #generate new help_table
    generate_help_table(SQL_FILEPATH, version)
    
    #print change to SQL_FILENAME
    new_file: str = read_new_table()
    print_change(old_file, new_file)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    taken = time.perf_counter() - start
    print(f"\n{CL_CYAN}Took {taken:.2f}s{CL_END}", end="")
