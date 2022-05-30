from gather import fetch_page

def main() -> None:
    page = fetch_page("https://mariadb.com/kb/en/insert/")
    #temporary write for testing features
    with open("test_page.txt", "w", encoding="utf-8") as outfile:
        outfile.write(page.text)

    return None

if __name__ == "__main__":
    main()