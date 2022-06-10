#imports
import re
import os
import time

from os.path import join as osjoin
from bs4 import BeautifulSoup
#classes
class Page:
    line_limit = 85
    forced_line_splits = 0
    def __init__(self, name, content) -> None:
        self.name = name
        self.content = content

        return None

    def format_text(self) -> None:
        """transforms the full html into stripped raw text for use in documentation"""
        #setup soup
        soup = BeautifulSoup(self.content, features="html5lib")
        #clean soup
        content = self.find_content(soup)
        content = self.clean_content(content)

        content = self.fix_tables(content)

        content = self.space_headers(content)
        content = self.space_code_blocks(content)
        #retrieve text
        text = content.get_text()
        #clean text
        text = self.set_line_limit(text)
        text = self.space_paragraphs(text)
        text = self.remove_extra_space(text)
        text = self.reduce_indents(text)
        #set text
        self.text = text
        
        return None

    def find_content(self, soup) -> BeautifulSoup:
        """Finds the relevant content in the webpage"""
        #find main content
        content = soup.find("section", {"id": "content"})

        return content

    def clean_content(self, content) -> BeautifulSoup:
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
        remove(content, "h2", {"id": "see-also"}) #remove see also header
        remove(content, "ul") #remove list items (potentially temporary- to remove elements under see-also)
        remove(content, "div", {"class": "mariadb"}) #remove mariadb version notices

        remove(content, "h1") #remove main header
        
        return content

    def fix_tables(self, content) -> BeautifulSoup:
        #find the tables
        tables = content.find_all("tbody")

        #for each table

        for table in tables:
            structured_table = self.create_table(table)
            text = self.format_table(structured_table)
            #table.tbody.decompose()
            table.string = text

        return content

    def create_table(self, table) -> list:
        trs = table.find_all("tr")
        columns = []
        for tr in trs:
            columns.append([])
            ths = tr.find_all("th") + tr.find_all("td")
            for th in ths:
                text = th.get_text()
                columns[-1].append(text)

        return columns

    def format_table(self, table) -> str:

        #get the maximum width for an element in the table
        max_width = 0
        for c in table:
            for column_index, e in enumerate(c):
                length = len(e)
                max_width = max(length, max_width)

        #lambda function to add top and bottom border
        add_border = lambda max_width, column_index: "+" + "".join(["-" * max_width + "+" for _ in range(column_index+1)])

        #add text
        text = ""
        text += add_border(max_width, column_index) + "\n"

        for row in table:
            text += "|"
            for element in row:
                #make spacing consistent
                if len(element) < max_width:
                    element += " " * (max_width - len(element))

                text += element + "|"
            text += "\n"
        text += add_border(max_width, column_index)

        #return
        return text

    def space_headers(self, content) -> BeautifulSoup:
        """Modifies headers to have extra space and decoration"""
        for header in content.find_all("h2"):
            length = len(header.text)
            header.string = "\n" + header.text + "\n" + "-" * length

        for header in content.find_all("h3") + content.find_all("h5"):
            header.string = "\n" + header.text + "\n"

        return content

    def space_code_blocks(self, contents) -> BeautifulSoup:
        """Spaces code blocks to improve readability"""

        code_blocks = contents.find_all("pre", {"class": "fixed"})
        for cb in code_blocks:
            cb.string = cb.text + "\n"

        return contents

    def set_line_limit(self, text) -> str:
        """Assures lines do not extend past a certain length"""
        lines = []
        for line in text.split("\n"):
            line2 = line
            while len(line2) > self.line_limit:
                line1, line2 = self.seperate_line(line2, self.line_limit)
                lines.append(line1)

            lines.append(line2)
        
        new_text = "\n".join(lines)

        return new_text

    def seperate_line(self, line, line_limit) -> list:
        """returns the given string capped to the line_limit and returns the remaining string"""
        start = 0
        matches = list(re.finditer(" ", line))
        for i, m in enumerate(matches):
            prev_start = start
            start = m.start()
            if (start > line_limit) or (i + 1 == len(matches)):
                line1 = line[:prev_start]
                line2 = line[prev_start + 1:]
                break

        #force the split
        if len(matches) == 0:
            self.forced_line_splits += 1
            line1, line2 = line[:self.line_limit], line[line_limit+1:]

        return line1, line2

    def space_paragraphs(self, text) -> str:
        """Adds extra space for paragraphs to improve readability"""
        text = re.sub(r'([^.])\. *\n *([^\n])', r'\1.\n\n\2',text)

        return text

    def remove_extra_space(self, text) -> str:
        """Removes extra new lines in text"""
        text = re.sub(" *\n *\n[ \n]*", "\n\n", text)

        return text.strip()

    def reduce_indents(self, text) -> str:
        """"""
        lines = text.split("\n")
        nlines = []
        for l in lines:
            if l.startswith("  "):
                spaces = re.match(" +", l)[0]
                l = (" " * (len(spaces) // 2)) + l.strip() 
            nlines.append(l)
        
        output = ""
        for l in nlines:
            output += l + "\n"
        
        return output


def main():
    """goes through each .html file in fetched_pages and writes the text version"""
    files = [html_file.replace(".html", "") for html_file in os.listdir("fetched_pages") if html_file.endswith(".html")]
    #files = ["about-sphinxse"]
    calc_time = True
    forced_line_splits = 0
    time_taken = 0

    for name in files:

        if calc_time: start_time = time.perf_counter()
        filepath = osjoin("fetched_pages", name)
        #open html
        infile = open(filepath+".html", "r", encoding="utf-8")
        html = infile.read()
        infile.close()
        #get text
        page = Page(name, html)
        #add forced_line_splits
        forced_line_splits += page.forced_line_splits
        #print forced line splits
        if page.forced_line_splits > 0: print(f"{page.forced_line_splits} - forced line splits - {page.name}")
        #write text
        outfile = open(filepath+".txt", "w", encoding="utf-8")
        outfile.write(page.text)
        outfile.close()
        #debug bug
        if calc_time: time_taken += time.perf_counter() - start_time

    print()
    print(f"{forced_line_splits} - TOTAL FORCED LINE SPLITS - {forced_line_splits}")
    print(f"Took {round(time_taken, 2)}s to run {len(files)} files")
    print(f"Avg of {round(time_taken / len(files), 3)}s per file")

if __name__ == "__main__":
    main()