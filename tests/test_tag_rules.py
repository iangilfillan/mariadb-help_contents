#imports
from bs4 import BeautifulSoup as Soup

#functions
def test_paragraphTag_():
    from lib.tag_rules import paragraphTag
    tag = Soup(
"""    <p>testing... testing...  

testing... testing...
testing...
testing...</p>
""", features="lxml")
    paragraphTag(tag)
    output = tag.string
    expected_output = "testing... testing... testing... testing... testing... testing..."
    assert output.strip() == expected_output

def test_headerTag():
    from lib.tag_rules import headerTag

    base: str = "<h0>Header0</h0>"

    for i in range(1, 7):
        string = base.replace('0', str(i))

        tag = Soup(string, features="lxml")
        headerTag(tag)

        output = tag.string
        expected_output = f"\nHeader{i}\n-------\n"

        assert output == expected_output

def test_codeTag():
    from lib.tag_rules import codeTag

    tag: Soup = Soup(
        "    <code>code</code>",
        features="lxml")

    codeTag(tag)
    output = tag.string

    expected_output = "\n\ncode\n"
    assert output == expected_output

def test_listTag():
    from lib.tag_rules import listTag

    tag: Soup = Soup(
        "    <li>Point One</li>",
        features="lxml"
        )
    listTag(tag)
    output = tag.string

    expected_output = "* Point One"
    assert output == expected_output

def test_tableTag():
    from lib.tag_rules import tableTag
    #TODO - Should cover a lot of edge cases
    
