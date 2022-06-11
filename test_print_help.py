#imports
import re
import os

#functions
def main() -> None:
    print("Help Table print test")
    help_table_file = get_help_table()
    help_structure = create_help_structure(help_table_file)
    run = True
    while run:
        Input = input("")
        if Input.lower()[0] == "q":
            print("Exited")
            break
        if not Input.upper().startswith("HELP ") or len(Input) < len("help _"):
            print("Invalid Syntax\n")
            continue
        requested_keyword = Input.upper().replace("HELP ", "").strip()
        if requested_keyword not in help_structure:
            print(f"Invalid Keyword ({requested_keyword})\n")
            continue
        description = help_structure[requested_keyword]
        print("\n\n\n\n\n\n\n\n\n\n")
        print(description, "\n")
    
    return None

def create_help_structure(help_table_file) -> dict:
    output = {}
    #read file
    infile = open(help_table_file, encoding="utf-8")
    lines = infile.readlines()
    infile.close()    
    #process lines
    for line in lines:
        #ignore non insert lines
        if not line.startswith("insert into help_topic (help_topic_id,help_category_id,name,description,example,url) values ("): continue
        #get info
        pattern = r"insert into help_topic \(help_topic_id,help_category_id,name,description,example,url\) values "
        pattern += r"\((\d+),(\d+),'(.*)','(.*)','()','(.*)'\)"
        help_topic_id, help_category_id, name, description, example, url = re.search(pattern, line).groups()
        #set description
        output[name] = description.replace("\\n", "\n")

    return output

def get_help_table() -> str:
    files = os.listdir()
    run = True
    while run:
        Input = input("Enter sql file: ")
        if Input in files: break
        else: print("File not found\n")
    
    return Input

if __name__ == "__main__":
    main()
