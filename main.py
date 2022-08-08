import timeit
import os
from lib.generate_help_table import generate_help_table

SEP = os.sep

SQL_FILENAME: str = "new_help_tables.sql"
SQL_FILEPATH: str = f"output{SEP}{SQL_FILENAME}"

def read_new_table():
    table = ""
    if SQL_FILENAME in os.listdir("output"):
        with open(SQL_FILEPATH, "r", encoding="utf-8") as sql_file:
            table = sql_file.read()

    return table

def print_change(old_file: str, new_file: str):
    if old_file == "":
        print("Wrote to", SQL_FILEPATH)
    elif old_file != new_file:
        print("Updated", SQL_FILEPATH)
    else:
        print("No change was made to", SQL_FILEPATH)

def main():
    #keep track of generated_table
    old_file = read_new_table()

    #generate new help_table
    generate_help_table(SQL_FILEPATH)
    
    #print change to SQL_FILENAME
    new_file = read_new_table()
    print_change(old_file, new_file)


if __name__ == "__main__":
    time = timeit.timeit(main, number=1)
    print(f"Took {time:.3f}s")
