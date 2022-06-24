#imports
import re
import os
import time
import sys

from os.path import join as osjoin
from bs4 import BeautifulSoup

#classes
class Page:
    line_limit = 79
    forced_line_splits = 0
    text = ""

    def __init__(self, name, content) -> None:
        self.name = name
        self.content = content

        return None

    def format_text(self) -> None:
        """transforms the full html into stripped raw text for use in documentation"""
        #setup soup
        html = self.content

        soup = BeautifulSoup(html, features="html5lib")
        #get main content
        content = self.find_content(soup)
        content = self.modify_content(content)
        #html manipulation
        html = str(content)
        html = self.remove_from_html(html)
        #text manipulation
        text = BeautifulSoup(html, features="html5lib").get_text()
        text = self.modify_text(text)
        #set text
        self.text = text
        
        return None

    def modify_content(self, content) -> BeautifulSoup:
        """Removes information from a BeautifulSoup object"""
        self.clean_content(content)
        self.fix_tables(content)
        self.space_headers(content)
        self.space_code_blocks(content)
        self.remove_extra_newlines(content)

        return content

    def remove_from_html(self, html):
        """Removes extra information at the bottom of the page"""
        #If examples is present
        index = html.find('<h2 class="anchored_heading" id="examples">')
        if index != -1:
            #Remove everything from the Examples heading
            html = html[:index]
            return html

        #If see also is present
        index = html.find('<h2 class="anchored_heading" id="see-also">')
        if index != -1:
            #Remove everything from the See Also heading
            html = html[:index]
            return html

        return html

    def modify_text(self, text) -> str:
        """Removes and modifies text"""
        text = self.set_line_limit(text)
        text = self.space_paragraphs(text)
        text = self.remove_extra_space(text)
        text = self.reduce_indents(text)
        #basic operations
        text = text.replace("'", r"\'")
        text = text.replace(r"\\'", r"\'")

        #add new lines for URL
        text += "\n" * 4
        #add URL
        url = "mariadb.com/kb/en/" + self.name + "/"
        text = text + "URL: " + url 

        return text

    def find_content(self, soup) -> BeautifulSoup:
        """Finds the relevant content in the webpage"""
        #find main content
        content = soup.find("section", {"id": "content"})
        
        return content

    def clean_content(self, content) -> None:
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
        #remove(content, "h2", {"id": "see-also"}) #remove see also header

        #remove(content, "div", {"class": "mariadb"}) #remove mariadb version notices

        #remove main header
        tag = content.find("h1")
        if tag != None: tag.decompose()

        return content

    def fix_tables(self, content) -> None:
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

    def equalise_table(self, table):
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

    def format_table(self, table):
        output = ""

        self.equalise_table(table)
        column_widths = self.get_column_widths(table)
        for row in table:
            str_line = self.add_row_break(column_widths)
            row_lines, number_of_lines = self.get_lines(row, column_widths)
            #print(row_lines)
            for i in range(number_of_lines):
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
        output += self.add_row_break(column_widths)
        return output

    def get_column_widths(self, table):
        row = table[0]

        lengths = []
        ratio = []

        for column in row:
            lengths.append(len(column))
        
        up_to = sum(lengths)
        
        column_widths = []
        for l in lengths:
            ratio = l / up_to
            c_width = self.line_limit - (3*len(lengths))
            c_width *= ratio
            column_widths.append(int(c_width))

        return column_widths

    def add_row_break(self, column_widths):
        row_break = "+"
        for i in column_widths:
            row_break += "-" * (i + 2) + "+"#(plus 2 to account for the two extra spaces)
        return row_break + "\n"

    def get_lines(self, row, column_widths):
        lines = []
        number_of_lines = 0
        for index, width in enumerate(column_widths):
            elines = self.sep_lines(row[index], width)
            lines.append(elines)
            number_of_lines = max(len(elines), number_of_lines)
        return lines, number_of_lines
    
    
    def sep_lines(self, string, len_line):
        lines = []
        line2 = string.strip()
        while len(line2) > len_line:
            line1, line2 = self.seperate_line(line2, len_line)
            lines.append(line1)
        lines.append(line2)

        return lines

    def space_headers(self, content) -> None:
        """Modifies headers to have extra space and decoration"""
        for header in content.find_all("h2"):
            length = len(header.text)
            header.string = "\n" + header.text + "\n" + "-" * length

        for header in content.find_all("h3") + content.find_all("h5"):
            header.string = "\n" + header.text + "\n"

    def space_code_blocks(self, content) -> None:
        """Spaces code blocks to improve readability"""

        code_blocks = content.find_all("pre", {"class": "fixed"})
        for cb in code_blocks:
            cb.string = cb.text + "\n"

    #transfer BeautifulSoup to text
    def remove_extra_newlines(self, content) -> None:
        """Removes new lines found in paragraphs where newlines are normally ignored"""
        for tag in content.find_all("p"):
            if not tag.parent.has_attr("fixed"):
                tag.string = tag.text.replace("\n", " ")
    #modify text

    def set_line_limit(self, text) -> str:
        """Assures lines do not extend past a certain length"""
        lines = []
        for line in text.split("\n"):
            line2 = line
            count = 0
            while len(line2) > self.line_limit:
                count += 1
                line1, line2 = self.seperate_line(line2, self.line_limit)
                lines.append(line1)
                #error, exits program
                if count > 100:
                    print(f"ERROR for LINE {line} in {self.name}")
                    exit()
            lines.append(line2)
        
        new_text = "\n".join(lines)

        return new_text

    def seperate_line(self, line, line_limit) -> list:
        """returns the given string capped to the line_limit and returns the remaining string"""

        matches = list(re.finditer(" ", line))
        for m in reversed(matches):
            start = m.start()
            if (start < line_limit):
                line1 = line[:start]
                line2 = line[start + 1:]
                break

        else:# len(matches) == 0:
            line1, line2 = line[:line_limit], line[line_limit+1:]

        return line1, line2

    def space_paragraphs(self, text) -> str:
        """Adds extra space for paragraphs to improve readability"""
        text = re.sub(r'([^.])\. *\n *([^\n])', r'\1.\n\n\2', text)

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
    files = set((html_file.replace(".html", "") for html_file in os.listdir("fetched_pages") if html_file.endswith(".html")))
    num_files = len(files)
    calc_time = True
    forced_line_splits = 0
    time_taken = 0

    print_line_splits = False
    if calc_time: start_time = time.perf_counter()
    for index, name in enumerate(files):

        filepath = osjoin("fetched_pages", name)
        #open html
        with open(filepath+".html", "r", encoding="utf-8") as infile:
            html = infile.read()
        #get text
        page = Page(name, html)
        page.format_text()
        #add forced_line_splits
        forced_line_splits += page.forced_line_splits
        #print forced line splits
        if page.forced_line_splits > 0 and print_line_splits: print(f"{page.forced_line_splits} - forced line splits - {page.name}")
        #write text
        with open(filepath+".txt", "w", encoding="utf-8") as outfile:
            outfile.write(page.text)
        #timing
        current_time_taken = time.perf_counter() - start_time
        current_avg_time = current_time_taken / (index+1)
        est_time_remaining = int(current_avg_time * (num_files - (index+1)))
        #debug
        sys.stdout.write(f"\rRan Through {index+1}/{num_files} files - (est time remaining: {est_time_remaining}s)")
        sys.stdout.flush()
    
    if calc_time: time_taken = time.perf_counter() - start_time

    print()
    print(f"{forced_line_splits} - TOTAL FORCED LINE SPLITS - {forced_line_splits}")
    print(f"Took {round(time_taken, 2)}s to run {num_files} files")
    print(f"Avg of {round(time_taken / num_files, 3)}s per file")


if __name__ == "__main__":
    main()