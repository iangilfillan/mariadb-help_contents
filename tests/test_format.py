import os
import re
from bs4 import BeautifulSoup

from lib.format_to_text import format_to_text

def test_clean_html():
    from lib.format_to_text import clean_html
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
    from lib.format_to_text import remove_see_also, clean_html
    with open(os.path.join("fetched_html", "alter-user.html"), encoding="utf-8") as infile:
        html_content = infile.read()
    
    html_content = clean_html(html_content)
    soup = BeautifulSoup(html_content, features="html5lib")
    remove_see_also(soup)
    html = str(soup)
    assert html.find('id: "see-also"') == -1


def test_modify_escape_characters():
    from lib.format_to_text import modify_escape_chars
    input_string = r"\'\\ \\\\\ \\ \\\\ \\ "
    output_string = modify_escape_chars(input_string)
    #check for cases where there are less than four backspaces in a row
    match = re.search(r"[^\\]\\\\[^\\]", output_string)
    assert not match

def test_escaped_G():
    from lib.format_to_text import modify_escape_chars
    input_string = r"\G\G\G\G"
    output_string = modify_escape_chars(input_string)
    #check for cases where there are less than four backspaces in a row
    assert output_string == r"\\G\\G\\G\\G"

def test_curly_quotes():
    from lib.format_to_text import modify_escape_chars
    input_string = "“”“”"
    output_string = modify_escape_chars(input_string)
    #check for cases where there are less than four backspaces in a row
    assert output_string == r'\"\"\"\"'

def test_format_full():
    from lib.format_to_text import format_to_text
    input_html = """
<title>test</title>
<section id="content" class="limited_width col-md-8 clearfix">
<p>This '\n' should go away</p>
<pre>This '\\n' should Become double</pre>
</section>
    """
    output_text = format_to_text(input_html, "test")
    expected_output = (
r"""This \' \' should go away\n\nThis \'\\n\' should Become double

URL: mariadb.com/kb/en/test/""")
    print(output_text)
    assert output_text == expected_output

def test_format_to_text():
    from lib.format_to_text import format_to_text, LINE_LIMIT
    """Tests all the requirements from format_to_text"""
    with open(os.path.join("fetched_html", "alter-user.html"), encoding="utf-8") as infile:
        html_content = infile.read()
    
    text = format_to_text(html_content, "alter-user")
    #test line limit
    lines = text.split("\\n")
    for l in lines:
        l = l.replace("\\'", "'")
        assert len(l) <= LINE_LIMIT
    #test number of newlines
    for l in lines:
        assert l.count("\n\n\n") == 0
    #


def test_reduce_indents():
    from lib.format_to_text import reduce_indents
    """Tests reduce_indents to make sure it doesn't remove content, and that it halves each line's indent"""
    text = (
"""
NoIndents
  TwoIndents
   ThreeIndents
    FourIndents
     FiveIndents
"""
    )
    expected_output = (
"""
NoIndents
 TwoIndents
 ThreeIndents
  FourIndents
  FiveIndents
"""
    )
    output = reduce_indents(text)
    assert output == expected_output

def test_add_url():
    from lib.format_to_text import add_url

    output = add_url(text="", name="test")
    expected_output = "\n\nURL: mariadb.com/kb/en/test/"

    assert output == expected_output

def test_remove_extra_newlines():
    from lib.format_to_text import remove_extra_newlines

    text = "01\n2\n\n3\n\n\n4\n\n\n\n5\n\n\n\n\n"
    output = remove_extra_newlines(text)
    expected_output = "01\n2\n\n3\n\n4\n\n5"

    assert output == expected_output