import re

from bs4 import BeautifulSoup

class Page:
    line_limit = 59
    def __init__(self, name, content) -> None:
        self.name = name
        self.content = content

        return None

    def format_text(self) -> None:
        #setup soup
        soup = BeautifulSoup(self.content, features="html5lib")
        #clean soup
        content = self.find_content(soup)
        content = self.clean_content(content)

        content = self.change_headers(content)
        #retrieve text
        text = content.get_text()
        #clean text
        text = self.set_line_limit(text)
        text = self.add_para_gaps(text)
        text = self.remove_spacing(text)
        #set text
        self.text = text
        
        return None

    def find_content(self, soup) -> BeautifulSoup:
        #find main content
        content = soup.find("section", {"id": "content"})

        return content

    def clean_content(self, content) -> BeautifulSoup:
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

    def change_headers(self, content) -> str:
        
        for header in content.find_all("h2"):
            length = len(header.string)
            header.string = "\n" + header.string + "\n" + "-" * length

        for header in content.find_all("h3") + content.find_all("h5"):
            header.string = "\n" + header.string + "\n"

        return content

    def set_line_limit(self, text) -> str:
        
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

    def add_para_gaps(self, text) -> str:
        
        text = re.sub(r'([^.])\. *\n *([^\n])', r'\1.\n\n\2',text)

        return text
    
    def remove_spacing(self, content) -> str:
        iterations = 0
        for _ in range(iterations):
            content = re.sub(r"\n *\n *\n", "\n\n", content)

        return content.strip()
