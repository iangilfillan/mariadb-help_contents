#imports
from os.path import join as osjoin
from gather import fetch_page

#functions
def main() -> None:
    list_of_urls = []
    for url in list_of_urls:
        #get page information
        page = fetch_page(url)
        #write to txt file
        filepath = osjoin("fetched_pages", page.name)
        outfile = open(f"{filepath}.txt", "w", encoding="utf-8")
        outfile.write(page.text)
        outfile.close()

    return None

#main call
if __name__ == "__main__":
    main()