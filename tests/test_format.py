import re
from pathlib import Path
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
    
    html_content = Path("fetched_html/alter-user.html").read_text(encoding="utf-8")
    
    html_content = clean_html(html_content)
    soup = BeautifulSoup(html_content, features="html5lib")
    remove_see_also(soup)
    html = str(soup)
    assert 'id: "see-also"' not in html

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

def test_ends_with_url():
    input_html = """
<title>test</title>
<section id="content" class="limited_width col-md-8 clearfix">
</section>
    """
    output_text = format_to_text(input_html, "test")
    expected_output = "URL: https://mariadb.com/kb/en/test/"
    assert output_text == expected_output

def test_format_full():
    input_html = """
<title>test</title>
<section id="content" class="limited_width col-md-8 clearfix">
<p>This '\n' should go away.</p>
<pre>This '\\n' should Become double.</pre>
</section>
    """
    output_text = format_to_text(input_html, "test")
    expected_output = (
r"This \' \' should go away.\n\n"\
r"This \'\\n\' should Become double."\
r"\n\nURL: https://mariadb.com/kb/en/test/"
)
    assert output_text == expected_output

def test_line_limit():
    from lib.format_to_text import LINE_LIMIT
    """Tests all the requirements from format_to_text"""
    html_content = Path("fetched_html/alter-user.html").read_text(encoding="utf-8")
    
    text = format_to_text(html_content, "alter-user")
    #test line limit
    lines = text.split(r"\n")
    for l in lines:
        l = l.replace(r"\'", "'")
        assert len(l) <= LINE_LIMIT

def test_linebreak_num():
    """Tests all the requirements from format_to_text"""
    html_content = Path("fetched_html/alter-user.html").read_text(encoding="utf-8")
    
    text = format_to_text(html_content, "alter-user")
    #test line limit
    lines = text.split(r"\n")
    for l in lines:
        assert "\n\n\n" not in l

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
    expected_output = "\n\nURL: https://mariadb.com/kb/en/test/"

    assert output == expected_output

def test_remove_extra_newlines():
    from lib.format_to_text import remove_extra_newlines

    text = "01\n2\n\n3\n\n\n4\n\n\n\n5\n\n\n\n\n"
    output = remove_extra_newlines(text)
    expected_output = "01\n2\n\n3\n\n4\n\n5"

    assert output == expected_output