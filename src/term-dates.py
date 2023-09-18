import requests
import datetime
import icalendar
import utils
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


def convert_to_date_obj(s: str) -> datetime.date:
    """
    Converts a date string to a `datetime.date` object.

    e.g. `"24 September 2023"` -> `datetime.date(2023, 9, 24)`
    """
    number = s.split()[0]

    # We need to left-pad the day number so that we can use strptime
    if len(number) == 1:
        s = "0" + s

    datetime_obj = datetime.datetime.strptime(s, "%d %B %Y")
    return datetime_obj.date()


def format_raw_term_date_data(raw):
    formatted = {}

    for old_entry in raw:
        term = old_entry["Term"]
        start = convert_to_date_obj(old_entry["Start"])
        end = convert_to_date_obj(old_entry["End"])

        formatted[term] = {"Start": start, "End": end}

    return formatted


def get_ical(formatted):
    cal = icalendar.Calendar()

    for name, dates in formatted.items():
        for date_type, dtstart in dates.items():
            event = icalendar.Event()

            summary = f"{date_type} of {name}"

            # For an event to show up as being an all-day event,
            # the DTEND has to be the day after the DTSTART
            dtend = dtstart + datetime.timedelta(days=1)

            event.add("summary", summary)
            event.add("dtstart", dtstart)
            event.add("dtend", dtend)

            cal.add_component(event)

    return cal


def main():
    raw = scrape_raw_term_date_data()
    formatted = format_raw_term_date_data(raw)
    utils.write_to_ics(get_ical(formatted), "term-dates")


if __name__ == "__main__":
    main()
