import os

from bs4 import BeautifulSoup
from src.page import clean_html, remove_see_also, format_to_text, LINE_LIMIT

def test_clean_html():
    html_input = (
"""
<html>
<head>
</head>
<body>
<div>
<section id="content" class="limited_width col-md-8 clearfix">
<h1>PAGE</h1>
</section>
</div>
</body>
</html>
"""
    )
    
    result = clean_html(html_input)

    correct_result = '<section id="content" class="limited_width col-md-8 clearfix">\n<h1>PAGE</h1>\n</section>'
    assert result == correct_result

def test_remove_see_also():
    with open(os.path.join("fetched_pages", "alter-user.html"), encoding="utf-8") as infile:
        html_content = infile.read()
    
    html_content = clean_html(html_content)
    soup = BeautifulSoup(html_content, features="html5lib")
    remove_see_also(soup)
    html = str(soup)
    assert html.find('id: "see-also"') == -1

def test_format_to_text():
    """Tests all the requirements from format_to_text"""
    with open(os.path.join("fetched_pages", "alter-user.html"), encoding="utf-8") as infile:
        html_content = infile.read()
    
    text = format_to_text(html_content, "alter-user")
    #test line limit
    lines = text.split("\n")
    for l in lines:
        l = l.replace("\\'", "'")
        assert len(l) <= LINE_LIMIT
    #test number of newlines
    for l in lines:
        assert l.count("\n\n\n") == 0
    #