# mariadb-help_contents

# INCOMPLETE README !!!

## Overview
The purpose of this project is to gather raw text from numerous pages in the mariadb.com/kb/en/ website to automatically update the documentation in the help files. 

## Next Goals
This will list the current short-term objectives for each version of the program 

## Repository Structure

the 'current_text_files' directory contains the text currently in 'fill_help_tables.sql' adjusted to be more readable
the 'fetched_pages' directory contains the KB's webpages and contains the text files generated from those webpages
the 'src' directory contains all the py files

'main'.py currently doesn't do anything

'page.py' currently goes through each .html file in 'fetched_pages' and generates the text

'insert_help_tables.py' currently goes through each line in the 'fill_help_tables.sql' file, finds the html file, generates the txt file, and replaces the description with the new text. This is written to 'new_help_tables.sql'