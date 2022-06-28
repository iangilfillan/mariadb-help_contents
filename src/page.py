#imports
import re
import os

from time import perf_counter
from os.path import join as osjoin
from bs4 import BeautifulSoup as Soup

#classes
LINE_LIMIT = 79

def format_to_text(html: str, name: str) -> str:
    """transforms the full html into stripped raw text for use in documentation"""
    #clean html
    html = clean_html(html)
    #setup soup
    content = Soup(html, features="html5lib")
    clean_content(content)

    tag_rules = [
        codeTag,
        headerTag,
        tableTag,
        listTag,
        paragraphTag,
    ]

    modify_tags(content, tag_rules)
    remove_see_also(content)
    #text
    text = content.get_text()
    text = modify_text(content.get_text())
    text = add_url(text, name)
    #set text
    return text

def clean_html(html: str) -> str:
    """Cleans up html so beautifulsoup has to do less processing"""
    section = html.find('<section id="content" class="limited_width col-md-8 clearfix">')
    if section == -1: return html

    end_section = html.find('</section>')
    if end_section == -1: return html

    html = html[section: end_section + len('</section>')]
    return html

def clean_content(content: Soup):
    """Removes irrelevant content still left in the webpage"""
    #helper method for easy removal
    def remove(content, *args, **kwargs):
        _ = [tag.decompose() for tag in content.find_all(*args, **kwargs) if tag != None]

    #remove irrelevant information
    remove(content, "div", {"id": "content_disclaimer"}) #removes a disclaimer
    remove(content, "div", {"id": "comments"}) #remove the comments
    remove(content, "h2", text = "Comments") #remove the comments' header
    remove(content, "div", {"id": "subscribe"}) #removes the subscribe thingy (I don't know what this removes)
    remove(content, "div", {"class": "simple_section_nav"}) #removes extra links

    remove(content, "div", {"class": "table_of_contents"}) #remove side contents bar

    #remove main header
    tag = content.find("h1")
    if tag is not None: tag.decompose()


def modify_tags(content: Soup, tag_rules: list):
        """Removes information from a BeautifulSoup object"""
        for modification in tag_rules:
            modification(content)

def remove_see_also(content: Soup):
    for n in range(2, 6):
        see_also = content.find(f"h{n}", {"id": "see-also", "class": "anchored_heading"})
        if see_also is not None:
            ns = see_also.find_next_sibling()
            if ns is not None: ns.decompose()
            see_also.decompose()

def modify_text(text: str) -> str:
    """Removes and modifies text"""
    text = set_line_limit(text)
    text = remove_extra_newlines(text)
    text = reduce_indents(text)
    text = modify_escape_chars(text)
    return text

def add_url(text, name):
    text += "\n" * 4 + "URL: "#add URL
    url = "mariadb.com/kb/en/" + name + "/"
    return text + url

def listTag(content):
    """Marks <li> items with a *"""
    lis = content.find_all("li")
    for li in lis:
        li.string = "* " + li.text

def tableTag(content):
    """Turns html tables into text tables"""
    #find the tables
    tables = content.find_all("tbody")

    #for each table
    for table in tables:
        structured_table = create_table(table)
        text = format_table(structured_table)
        #table.tbody.decompose()
        table.string = "\n" + text


#creating a table
def create_table(table) -> list:
    """Creates a table"""
    trs = table.find_all("tr")
    columns = []
    for tr in trs:
        columns.append([])
        ths = tr.find_all("th") + tr.find_all("td")
        for th in ths:
            text = th.get_text()
            columns[-1].append(text)

    return columns

def equalise_table(table):
    """makes sure there are no rows with less columns than other rows"""
    max_row_length = 0
    for row in table:
        row_length = len(row)
        max_row_length = max(max_row_length, row_length)

    for row in table:
        row_length = len(row)
        if row_length < max_row_length:
            row += [""] * (max_row_length - row_length)

    return table

def format_table(table):
    """Formats a table from a list into raw text"""
    output = ""

    equalise_table(table)
    column_widths = get_column_widths(table)
    for row in table:
        str_line = add_row_break(column_widths)
        row_lines, num_lines = get_lines(row, column_widths)
        #print(row_lines)
        for i in range(num_lines):
            str_line += "|"
            for index, line in enumerate(row_lines):
                str_line += " "
                if i < len(line):
                    str_line += line[i] + " " * (column_widths[index] - len(line[i]))
                else:
                    str_line += " " * column_widths[index]
                str_line += " |"
            str_line += "\n"
        output += str_line
    output += add_row_break(column_widths)
    return output

def get_column_widths(table: list) -> list:
    """Gets the required width for each column"""
    row: list = table[0]
    lengths: list = [len(column) for column in row]

    sum_lengths: int = sum(lengths)
    total_width: int = LINE_LIMIT - (3*len(lengths))
    #total width times the ratio of length / the sum of lengths
    column_widths = [int(total_width * (l / sum_lengths)) for l in lengths]

    return column_widths

def add_row_break(column_widths: str) -> str:
    """Breaks up rows with dashes and pluses"""
    #+-----+-----+-----+
    row_break = "+" + "".join(["-" * (width + 2) + "+" for width in column_widths])
    return row_break + "\n"

def get_lines(row: list, column_widths: list) -> tuple((list, int)):
    """returns the rows of lines and the number of lines for the column"""
    rows = []
    num_lines = 0
    for index, width in enumerate(column_widths):
        lines = sep_lines(row[index].strip(), width)
        rows.append(lines)
        num_lines = max(len(lines), num_lines)
    
    return rows, num_lines

def sep_lines(string, len_line):
    """Seperates the lines based on the given length"""
    lines = []
    line2 = string
    while len(line2) > len_line:
        line1, line2 = seperate_line(line2, len_line)
        lines.append(line1)
    lines.append(line2)

    return lines
#header tag
def headerTag(content):
    """Modifies headers to have extra space and decoration"""
    headers = []
    for num in range(2, 6):
        headers += content.find_all(f"h{num}")

    for header in headers:
        length = len(header.text)
        header.string = "\n" + header.text + "\n" + "-" * length + "\n"

def codeTag(content):
    """Spaces code blocks to improve readability"""

    code_blocks = content.find_all("pre", {"class": "fixed"})
    for cb in code_blocks:
        cb.string = "\n\n" + cb.text + "\n"

#modify text
def set_line_limit(text) -> str:
    """Assures lines do not extend past a certain length"""
    #recreate the text
    lines = []
    for line in text.split("\n"):
        lines += sep_lines(line, LINE_LIMIT)

    new_text = "\n".join(lines)

    return new_text

def seperate_line(line, line_limit) -> list:
    """returns two split based on the line limit"""
    #get an index for each space in the line
    matches = list(re.finditer(" ", line))
    #iterate through each space from the top
    for m in reversed(matches):
        start = m.start()
        #if the space is within the line limit
        if (start < line_limit):
            #split the line at that space's index
            line1 = line[:start]
            line2 = line[start + 1:]
            break
    #if no splits were made
    else:
        #force a split at the line limit
        line1, line2 = line[:line_limit], line[line_limit+1:]

    return line1, line2

def paragraphTag(content: Soup):
    
    p_tags = content.find_all("p")
    for p in p_tags:
        p.string = p.text.strip().replace("\n", " ").replace("  ", " ") + "\n"

def remove_extra_newlines(text) -> str:
    """Replaces all groups of newlines with a max of 2"""
    text = re.sub(" *\n *\n[ \n]*", "\n\n", text)

    return text.strip()

def reduce_indents(text: str) -> str:
    """"""
    lines = text.split("\n")

    nlines = []
    for l in lines:
        if l.startswith("  "):
            spaces = re.match(" +", l)[0]
            l = (" " * (len(spaces) // 2)) + l.strip() 
        nlines.append(l)
    
    output = "\n".join(nlines)
    return output

def modify_escape_chars(text: str) -> str:
    """escape character nonsense"""
    text = text.replace("'", r"\'")
    text = text.replace(r"\\'", r"\'")
    text = text.replace(r"\\", r"\\\\")

    return text

def main():
    """goes through each .html file in fetched_pages and writes the text version"""
    files = [html_file.replace(".html", "") for html_file in os.listdir("fetched_pages") if html_file.endswith(".html")]
    num_files = len(files)
    time_taken = 0

    start_time = perf_counter()
    for index, name in enumerate(files):

        filepath = osjoin("fetched_pages", name)
        #read html
        with open(filepath+'.html', 'r', encoding='utf-8') as inf: html = inf.read()
        #format html to text
        text = format_to_text(html, name)
        #write out text
        with open(filepath+".txt", "w", encoding="utf-8") as outf: outf.write(text)
        #debug over same line
        print(f"\rRan Through {index+1}/{num_files} files", end="")
    
    time_taken = perf_counter() - start_time

    print()
    print(f"Took {round(time_taken, 2)}s to run {num_files} files")
    print(f"Avg of {round(time_taken / num_files, 3)}s per file")

    return time_taken

if __name__ == "__main__":
    main()