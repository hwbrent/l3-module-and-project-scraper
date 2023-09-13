import utils
from selenium.webdriver.common.by import By

URL = "https://mytimetable.durham.ac.uk/weekly/activities"

WEEK_PATTERNS_URL = "https://timetable.dur.ac.uk/week_patterns.htm"


def scrape_raw_week_patterns(driver) -> list[dict]:
    """
    Scrapes the week pattern data and returns it in a `list` of `dict`s,
    where each `dict` represents a week (or a row in the `<table>` found
    on the week patterns webpage).
    """
    utils.login_to_page_with_url_auth(driver, WEEK_PATTERNS_URL)

    # This is the structure of the table:
    # +–––––––––––––––––––––––––––––+––––––––––––––––––––––+
    # |       Syllabus Weeks        |   Durham Weeks       |
    # +–––––––––––––+–––––––––––––––+––––––+–––––––––––––––+
    # | Week Number | Calendar Date | Term | Teaching Week |
    # +–––––––––––––+–––––––––––––––+––––––+–––––––––––––––+
    # |    Week 1   |               |      |               |
    # +-------------+---------------+------+---------------+
    # etcetera

    # "Syllabus Weeks", "Durham Weeks", "Week Number", "Calendar Date"
    # "Term", and "Teaching Week" are all in their own <th> elements.
    all_headers = []
    for th in driver.find_elements(By.TAG_NAME, "th"):
        header = th.text.strip()
        all_headers.append(header)

    # This is just the "Week Number", "Calendar Date", "Term", and "Teaching Week"
    col_headers = all_headers[2:]

    data = []

    # • The date info is stored in <tr>s in the overall <table>.
    # • The first two <tr>s are in the table header, so we ignore those.
    trs = driver.find_elements(By.TAG_NAME, "tr")
    for tr in trs[2:]:
        row_data = {}

        # Each <tr> has one <td> for each column
        tds = tr.find_elements(By.TAG_NAME, "td")

        for header, td in zip(col_headers, tds):
            cell_value = td.text.strip()
            row_data[header] = cell_value
        data.append(row_data)

    return data


def main():
    driver = utils.get_driver()
    utils.login_to_page(driver, URL)

    input()

    driver.quit()


if __name__ == "__main__":
    main()
