"""Version selecting and debug info, interface to run generation script"""
import time
import sys, os
from pathlib import Path
from lib.generate_help_table import generate_help_table
import lib.debug as debug
from lib.version import Version
# Preparing system for colored text
os.system('')
# Path to output sql file
SQL_FILEPATH: Path = Path("output/fill_help_tables.sql")

# Functions
def get_version() -> Version:
    """Reads the version number while giving precise debug info"""
    if len(sys.argv) < 2:
        debug.error("Must give a Version number!")
    
    version_str: str = sys.argv[1]
    assert version_str.isnumeric()
    assert len(version_str) >= 3
    version = Version.from_str(sys.argv[1])
    assert version.major >= 10
    return version
    
    # elif sys.argv[1][0] == '1' and len(sys.argv[1]) == 1:
    #     debug.warn(f"Version '1' results in incorrect HELP_VERSION")
    #     version = int(sys.argv[1])
    # elif not sys.argv[1].isnumeric():
    #     debug.error("Invalid version argument")
    # elif sys.argv[1] == '0':
    #     debug.error("Cannot have 0 as version number!")
    # elif len(sys.argv[1]) not in [3, 4]:
    #     debug.error("Version number must of length 3 or 4 (eg: 105, 1010)")
    # elif sys.argv[1][0] != "1":
    #     debug.error("Version must start with '1' (eg: 105, 1010)")
    # elif sys.argv[1][1] != "0":
    #     debug.warn("Versions above 10.x not accounted for")
    #     version = int(sys.argv[1])
    # elif int(sys.argv[1][2:]) < 3:
    #     debug.warn("Versions below 10.3 have no effect")
    #     version = int(sys.argv[1])
    # else:
    #     version = int(sys.argv[1])
    
    # return version

def get_concat_size() -> int:
    default = 15000
    min_concat = 1000
    if len(sys.argv) < 3:
        return default
    
    if not sys.argv[2].isnumeric():
        debug.error("Invalid Concat Size")
    if int(sys.argv[2]) < min_concat:
        debug.error(f"Concat Size Too Small (min={min_concat})")

    return int(sys.argv[2])

def read_new_table() -> str:
    """Reads output SQL file.
       Returns empty string if failed to read"""
    if SQL_FILEPATH.exists():
        return SQL_FILEPATH.read_text(encoding="utf-8")
    return ""

def print_change(old_file: str, new_file: str):
    """Checks whether SQL file has been modified"""
    if not old_file:
        debug.info(f"Wrote to {SQL_FILEPATH}")
    elif old_file != new_file:
        debug.info(f"Updated {SQL_FILEPATH.name}")
    else:
        debug.info(f"No change was made to {SQL_FILEPATH}")

def check_max_char_length(sql: str, concat_size: int):
    max_line_length = 0
    index = 0
    for index, line in enumerate(sql.splitlines(), 1):
        # max line length
        if len(line) > concat_size:
            debug.warn(f"Line {index} above {concat_size}: ({len(line)})")
        max_line_length = max(max_line_length, len(line))
        # even number of single quotes
        if line.replace("\\'", "").count("'") % 2 != 0:
            debug.warn(f"Line {index} uneven number of single quotes")
        #
        
    debug.info(f"Number of Lines: {index}")
    debug.info(f"Max Line Length: {max_line_length}")

def main():
    #keep track of generated_table
    old_file = read_new_table()
    
    #retrive version
    version = get_version()
    concat_size: int = get_concat_size()
    debug.success(f"Selected Version: {version}")
    debug.success(f"Selected Concat Size: {concat_size}")
    #generate new help_table
    generate_help_table(SQL_FILEPATH, version, concat_size-400) #makes room for line info around description
    
    #print change to SQL_FILENAME
    new_file = read_new_table()
    print_change(old_file, new_file)
    check_max_char_length(new_file, concat_size)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    taken = time.perf_counter() - start
    debug.time_info(f"Took {taken:.2f}s")