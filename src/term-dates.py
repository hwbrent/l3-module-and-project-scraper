import requests
from bs4 import BeautifulSoup
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

URL = "https://www.durham.ac.uk/academic-dates/"


def scrape_raw_term_date_data():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # The data is stored in a <table>. It looks something like this:
    # + -------------------- + ----------------- + ----------------- +
    # | Term                 | Start             | End               |
    # + -------------------- + ----------------- + ----------------- +
    # | Summer Vacation 2023 | 24 June 2023      | 24 September 2023 |
    # + -------------------- + ----------------- + ----------------- +
    # | Induction Week 2023  | 25 September 2023 | 1 October 2023    |
    # + -------------------- + ----------------- + ----------------- +
    # | ...                  | ...               | ...               |
    # + -------------------- + ----------------- + ----------------- +
    # Turns out it's the first table in the document.
    data_table = soup.find("table")

    # The header/column names are in <th> elements within the table's <thead>
    header_ths = data_table.find_all("th")
    header_names = [th.text for th in header_ths]

    data = []

    # More specifically, each term's start/end data is stored in a <tr>
    rows = data_table.find_all("tr")

    # Ignore the first row; it contains the <th>s, which we've dealt with already
    for row in rows[1:]:
        cells = row.find_all("td")
        values = [cell.text for cell in cells]

        row_data = {}
        for header_name, value in zip(header_names, values):
            row_data[header_name] = value

        data.append(row_data)

    return data


def main():
    term_dates = scrape_raw_term_date_data()
    pp.pprint(term_dates)


if __name__ == "__main__":
    main()
