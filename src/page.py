import re

from bs4 import BeautifulSoup

class Page:
    line_limit = 59
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

        content = self.space_headers(content)
        content = self.space_code_blocks(content)
        #retrieve text
        text = content.get_text()
        #clean text
        text = self.set_line_limit(text)
        text = self.space_paragraphs(text)
        #strip and set text
        self.text = text.strip()
        
        return None

    def find_content(self, soup) -> BeautifulSoup:
        """Finds the relevant content in the webpage"""
        #find main content
        content = soup.find("section", {"id": "content"})

        return content

    def clean_content(self, content) -> BeautifulSoup:
        """Removes irrelevant content still left in the webpage"""
        #helper method
        def remove(content, *args, **kwargs):
            tag = content.find(*args, **kwargs)
            if tag != None:
                tag.decompose()
        
        #remove irrelevant information
        remove(content, "div", {"id": "content_disclaimer"})
        remove(content, "div", {"id": "comments"})
        remove(content, "h2", text = "Comments")
        remove(content, "div", {"id": "subscribe"})
        remove(content, "div", {"class": "simple_section_nav"})
        #remove side contents bar
        remove(content, "div", {"class": "table_of_contents"})
        #remove see also
        remove(content, "h2", {"id": "see-also"})
        #remove list items
        #remove mariadb version notices
        remove(content, "div", {"class": "mariadb"})

        remove(content, "ul")
        #remove main header
        remove(content, "h1")
        return content

    def space_headers(self, content) -> str:
        """Modifies headers to have extra space and decoration"""
        for header in content.find_all("h2"):
            length = len(header.string)
            header.string = "\n" + header.string + "\n" + "-" * length

        for header in content.find_all("h3") + content.find_all("h5"):
            header.string = "\n" + header.string + "\n"

        return content

    def space_code_blocks(self, contents) -> str:
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
        start = 0
        matches = list(re.finditer(" ", line))
        for i, m in enumerate(matches):
            prev_start = start
            start = m.start()
            if (start > line_limit) or (i + 1 == len(matches)):
                line1 = line[:prev_start]
                line2 = line[prev_start + 1:]

                break
        
        return line1, line2

    def space_paragraphs(self, text) -> str:
        """Adds extra space for paragraphs to improve readability"""
        text = re.sub(r'([^.])\. *\n *([^\n])', r'\1.\n\n\2',text)

        return text
