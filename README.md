# mariadb-help_contents


## Function

The script updates the sql file 'fill_help_tables' with the recent information in the mariaDB knowledge base.

This sql file contains raw text which is displayed when calling 'HELP' on an existing keyword


## Usage

'insert_help_tables.py' generates an sql file called 'new_help_tables.sql' from an existing sql file called 'fill_help_tables.py'.

'page.py' generates a .txt file for each html file contained in the 'fetched_pages' directory.

The scripts do not update the html contained in 'fetched_pages', you need to move the updated html there manually (hopefully temporary)

## Dependencies

Need a fairly recent python version (probably 3.7 and above, haven't tested)

Need the BeautifulSoup4 python library