"""Version selecting and debug info, interface to run generation script"""
import time
import sys, os
from pathlib import Path
from lib.generate_help_table import generate_help_table
import lib.debug as debug
# Preparing system for colored text
os.system('')
# Path to output sql file
SQL_FILEPATH: Path = Path("output/fill_help_tables.sql")

# Functions
def get_version() -> int:
    """Reads the version number while giving precise debug info"""
    if len(sys.argv) < 2:
        debug.error("Must give a Version number!")
    elif sys.argv[1][0] == '1' and len(sys.argv[1]) == 1:
        version = int(sys.argv[1])
        debug.success(f"Selected Version: {version}")
    elif not sys.argv[1].isnumeric():
        debug.error("Invalid version argument")
    elif sys.argv[1] == '0':
        debug.error("Cannot have 0 as version number!")
    elif len(sys.argv[1]) not in [3, 4]:
        debug.error("Version number must of length 3 or 4 (eg: 105, 1010)")
    elif sys.argv[1][0] != "1":
        debug.error("Version must start with '1' (eg: 105, 1010)")
    elif sys.argv[1][1] != "0":
        debug.warn("Versions above 10.x not accounted for")
    elif int(sys.argv[1][2:]) <= 3:
        debug.warn("Versions below 10.4 have no effect")
        version = int(sys.argv[1])
    elif sys.argv[1][2] == '0':
        debug.warn("Unecessary '0' for third digit")
        version = int(sys.argv[1])
    else:
        version = int(sys.argv[1])
        debug.success(f"Selected Version: {version}")
    
    # Extra newline for style points
    print()
    return version

def read_new_table() -> str|None:
    """Reads output SQL file"""
    if SQL_FILEPATH.exists():
        return SQL_FILEPATH.read_text(encoding="utf-8")

def print_change(old_file: str, new_file: str):
    """Checks whether SQL file has been modified"""
    if old_file == "":
        debug.info(f"Wrote to {SQL_FILEPATH}")
    elif old_file != new_file:
        debug.info(f"Updated {SQL_FILEPATH.name}")
    else:
        debug.info(f"No change was made to {SQL_FILEPATH}")

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
    debug.time_info(f"Took {taken:.2f}s")
