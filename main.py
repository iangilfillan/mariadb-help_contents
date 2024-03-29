"""Version selecting and debug info, interface to run generation script"""
import time
import sys, os
from pathlib import Path
from lib.generate_help_table import generate_help_table
import lib.debug as debug
from lib.version import Version
import argparse

# Preparing system for colored text
os.system('')

SQL_FILENAME: str = "fill_help_tables.sql"
DEFAULT_CONCAT_SIZE = 15000

def read_args() -> tuple[list[Version], int]:

    parser = argparse.ArgumentParser()
    parser.add_argument("--length", "-l", type=int, default=DEFAULT_CONCAT_SIZE)
    parser.add_argument("--versions", "--version", "-v", nargs="+", required=True)
    args = parser.parse_args()
    
    versions = read_versions(args.versions)
    return versions, args.length

# Functions
def read_versions(args: list[str]) -> list[Version]:
    """Reads the version number while giving precise debug info"""
    versions = []
    for version_str in args:
        assert version_str.isnumeric(), version_str
        assert len(version_str) >= 3
        version = Version.from_str(version_str)
        assert version.major >= 10
        versions.append(version)
    return versions

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
    versions, concat_size = read_args()
    debug.success(f"Selected Versions: {versions}")

    Path("output").mkdir(exist_ok=True)
    for version in versions:
        print()
        debug.success(f"Generating Version: {version}")
        output_filepath = Path("output") / f"fill_help_tables-{version.major}{version.minor}.sql"
        generate_help_table(output_filepath, version, concat_size-400) #makes room for line info around description
        new_file = output_filepath.read_text(encoding="utf-8")
        check_max_char_length(new_file, concat_size)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    taken = time.perf_counter() - start
    debug.time_info(f"Took {taken:.2f}s")