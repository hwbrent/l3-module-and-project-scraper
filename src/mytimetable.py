import utils
import re
import json
import icalendar
from urllib.parse import urlparse, parse_qs
from datetime import datetime, date, timedelta
from selenium.webdriver.common.by import By

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

URL = "https://mytimetable.durham.ac.uk/weekly/activities"

WEEK_PATTERNS_URL = "https://timetable.dur.ac.uk/week_patterns.htm"

# fmt: off
MONTHS = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# fmt: on


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


def format_week_number(raw: str) -> int:
    raw = raw.replace("Week ", "")
    return int(raw)


def format_teaching_week(raw: str):
    # If it's an empty string, return `None` to reflect this
    if raw == "":
        return None

    # If it's a teaching week, parse the number out of it and return that
    # as an `int`
    if "Teaching week" in raw:
        raw = raw.replace("Teaching week ", "")
        return int(raw)

    return raw


def format_calendar_date(raw: str, year: int) -> str:
    """
    Given a `raw` calendar date (e.g. `"Mon 11 Dec - Fri 15 Dec"`),
    this function returns a `str` in the ISO 8601 format representing the
    Monday (e.g. 2023-12-11).
    """
    start, _ = raw.split(" - ")

    _, day, month_raw = start.split()
    day = int(day)
    month = MONTHS.index(month_raw) + 1

    return date(year, month, day).isoformat()


def format_week_patterns(raw_data: list[dict], academic_year: str) -> list[dict]:
    formatted = []

    for i, old_entry in enumerate(raw_data):
        week_number, calendar_date, term, teaching_week = old_entry.values()

        if i > 0:
            prev_entry = raw_data[i - 1]
            prev_calendar_date = prev_entry["Calendar Date"]
            if "Dec" in prev_calendar_date and "Jan" in calendar_date:
                academic_year += 1

        # fmt: off
        formatted.append({
            "Week Number": format_week_number(week_number),
            "Calendar Date": format_calendar_date(calendar_date, academic_year),
            "Term": term or None,
            "Teaching Week": format_teaching_week(teaching_week)
        })
        # fmt: on

    return formatted


def scrape_raw_academic_year(driver) -> str:
    # It's located in a <div> with class 'l2sitename'. The innerText will
    # be something like "2023-24 Teaching Timetable"
    div = driver.find_element(By.CLASS_NAME, "l2sitename")
    raw = div.text.strip()
    return raw


def format_academic_year(raw):
    # `academic_year` will be something like "2023-24".
    # This replaces the dash and two digits with nothing, and leaves us with
    # the first year (e.g. 2023).
    raw = raw.replace(" Teaching Timetable", "")
    first_year = re.sub(r"-\d\d", "", raw)
    first_year = int(first_year)
    return first_year


def get_academic_year(driver):
    utils.login_to_page_with_url_auth(driver, WEEK_PATTERNS_URL)
    raw = scrape_raw_academic_year(driver)
    formatted = format_academic_year(raw)
    return formatted


def get_week_patterns(driver):
    raw = scrape_raw_week_patterns(driver)
    academic_year = get_academic_year(driver)
    clean = format_week_patterns(raw, academic_year)
    return clean


def day_has_activities(list) -> bool:
    """
    Indicates whether the list of activities provided actually contains any.
    """
    # If there are no activities, there will be an element
    # with class 'activity-none'
    try:
        list.find_element(By.CLASS_NAME, "activity-none")
        return False
    except:
        return True


def get_timetable_activities(driver, week_patterns):
    utils.login_to_page(driver, URL)

    for week_pattern in week_patterns:
        iso_date = week_pattern["Calendar Date"]

        # Show the timetable activites for the given week in the week patterns.
        # A parameter can be added to the URL - the parameter name is 'date', and the
        # value is a date in the ISO format (i.e. YYYY-MM-DD)
        week_page = f"{URL}?date={iso_date}"
        driver.get(week_page)

        # Monday, Tuesday, etc.
        days_h2s = driver.find_elements(By.TAG_NAME, "h2")
        days = (day.text.strip() for day in days_h2s)

        # Each day of the week has a <div> which in theory will contain its
        # activities. The <div> has class 'activity-list'
        activity_lists = driver.find_elements(By.CLASS_NAME, "activity-list")

        for index, (day, activity_list) in enumerate(zip(days, activity_lists)):
            exact_date = date.fromisoformat(iso_date) + timedelta(index)

            if not day_has_activities(activity_list):
                continue

            activities = activity_list.find_elements(By.CLASS_NAME, "activity")
            for activity in activities:
                # E.g. Seminar, Lecture, etc
                kind = activity.find_element(By.CLASS_NAME, "activity-type-title").text

                time_raw = activity.find_element(By.CLASS_NAME, "activity-time").text
                time = time_raw.split(" - ")

                sections = activity.find_elements(By.CLASS_NAME, "activity-section")
                name_div, location_div, staff_div = sections

                name = name_div.find_element(By.XPATH, "./div[2]").text.strip()

                location_a = location_div.find_element(By.TAG_NAME, "a")
                room = location_a.text.strip()
                gmaps_link = location_a.get_attribute("href").strip()

                staff = staff_div.find_element(By.XPATH, "./div[2]").text.strip()

                yield {
                    "Type": kind,
                    "Time": time,
                    "Name": name,
                    "Location": [room, gmaps_link],
                    "With": staff,
                    "Date": exact_date.isoformat(),
                    "Day of the Week": day,
                    "Timetable URL": driver.current_url,
                    "Week": week_pattern,
                }


def get_ical(activities):
    cal = icalendar.Calendar()

    for activity in activities:
        event = icalendar.Event()

        # 'Date': '2023-10-02',
        # 'Day of the Week': 'Monday',
        # 'Location': [
        #     'D/ERA30',
        #     'https://www.google.com/maps/search/?api=1&query=54.77463142032579%2C-1.5720368995935576'
        # ],
        # 'Name': 'CFLS1G21 - German Stage 2',
        # 'Time': [
        #     '11:00',
        #     '12:00'
        # ],
        # 'Timetable URL': 'https://mytimetable.durham.ac.uk/weekly/activities?date=2023-10-02',
        # 'Type': 'Seminar',
        # 'Week': {
        #     'Calendar Date': '2023-10-02',
        #     'Teaching Week': 1,
        #     'Term': 'Michaelmas',
        #     'Week Number': 12},
        #     'With': 'MRS ZHANNA KOZMENKO-IHSSEN'
        # }

        # Format value for SUMMARY
        kind = activity["Type"]
        name = activity["Name"]
        summary = f"{kind}: {name}"

        location, gmaps_link = activity["Location"]
        # Format value for GEO.
        # This has to be a semicolon-separated pair of floating point numbers.
        # We can use the latitude and longitude from the Google Maps link for
        # this.
        parsed_url = urlparse(gmaps_link)
        query_params = parse_qs(parsed_url.query)
        raw_geo = query_params.get("query", None)[0]
        latitude_str, longitude_str = raw_geo.split(",")
        latitude = float(latitude_str)
        longitude = float(longitude_str)
        geo = icalendar.vGeo((latitude, longitude))

        # Format value for DTSTART and DTEND
        date = activity["Date"]  # e.g. '2023-10-02'
        start, end = activity["Time"]  # e.g. '11:00' and '12:00'
        dtstart = datetime.fromisoformat(f"{date}T{start}")
        dtend = datetime.fromisoformat(f"{date}T{end}")

        event.add("summary", summary)
        event.add("location", location)
        event.add("geo", geo)
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)

        cal.add_component(event)

    print(cal.to_ical().decode("utf-8"))

    return cal


def main():
    # driver = utils.get_driver()
    # week_patterns = get_week_patterns(driver)
    # activities = [a for a in get_timetable_activities(driver, week_patterns)]
    # driver.quit()
    # utils.write_to_json(activities, "mytimetable")

    with open("mytimetable(individual).json", "r") as f:
        get_ical(json.load(f))


if __name__ == "__main__":
    main()
