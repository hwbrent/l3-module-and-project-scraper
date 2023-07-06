from pprint import PrettyPrinter

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By

pp = PrettyPrinter(indent=4)

from utils import (
    get_driver,
    login_to_page_with_url_auth,
    get_parent,
    get_previous_sibling,
)

MODULE_TIMETABLE_URL = "https://timetable.dur.ac.uk/module.htm"


# --------------------


def get_module_params(driver) -> list[dict[str, str]]:
    """
    This function navigates to `MODULE_TIMETABLE_URL`, and scrapes & returns the
    data within the <select> and <option> elements.

    These elements' values are used to send to the server to get the
    module timetable which is why we want this data (obviously).
    """

    login_to_page_with_url_auth(driver, MODULE_TIMETABLE_URL)

    param_fields = []

    # The different selection options are stored in <select> elements, each
    # of which has multiple <option> elements which store the user-facing
    # keys and values of the available parameters.

    selects = driver.find_elements(By.TAG_NAME, "select")
    for select in selects:
        # The internal (i.e. not user-facing) name of the <select>.
        # It does give some insight into how the <option>'s are used,
        # but ideally we want to get the label for this <select>.
        name = select.get_attribute("name")

        # This <select> is located within a <table>. More specifically, it's
        # a <td> within a <tr>. And the previous <td> sibling to this <td>
        # is the <td> whose inner text is the label that we want.
        parent_td = get_parent(select)
        sibling_td = get_previous_sibling(parent_td)
        label = sibling_td.text

        subfield_params = {}

        options = select.find_elements(By.TAG_NAME, "option")
        for option in options:
            # The <option> element has two values that we care about.
            # The first is its "value" attribute which stores the value that
            # the server will recognise.
            # The second is the innerText value, which is what the user sees.
            # e.g: <option value="44">w/c Mon 13 May 2024 - week 44</option>

            key = option.text
            value = option.get_attribute("value")

            subfield_params[key] = value

        param_fields.append({"name": name, "label": label, "values": subfield_params})

    return param_fields


def get_timetable_page(driver, choices: dict[str, list[str]]) -> None:
    """
    This function goes to the timetable page corresponding to the choices
    (i.e. the selected `<option>`s' values) in `choices`.
    """
    login_to_page_with_url_auth(driver, MODULE_TIMETABLE_URL)

    # Basically what we're doing is:
    # - Getting the 'value' attribute of each <option> chosen (this data is)
    #   passed in via the 'choices' parameter.
    # - Using JavaScript to find that <option> in the DOM and set its
    #   "selected" attribute to be 'true' (because you can't do this with
    #   Selenium).
    # - Clicking the "View Timetable" button.

    for _, option_values in choices.items():
        for option_value in option_values:
            driver.execute_script(
                f'document.querySelector(`[value="{option_value}"]`).selected = true;'
            )

    # Click the "submit" button
    view_timetable_button = driver.find_element(
        By.CSS_SELECTOR, 'input[value="View Timetable"]'
    )
    view_timetable_button.click()


def parse_activity_data(table):
    activity_data = []

    rows = table.find_all("tr")

    # Handle cases where there are no activities on a certain day
    if len(rows) == 0:
        return activity_data

    thead = rows[0]
    column_names = tuple(cell.text.strip() for cell in thead.find_all("td"))

    tbody = rows[1:]
    for row in tbody:
        entry = {}

        cells = row.find_all("td")
        for i, cell in enumerate(cells):
            column_name = column_names[i]
            value = cell.text.strip()

            entry[column_name] = value

        activity_data.append(entry)

    return activity_data


def parse_raw_module_data(data):
    module_data = {}

    # • We want to iterate over pairs in `raw`
    # • i.e. (0,1), (2,3), (4,5), (6,7) etc
    for i in range(0, len(data) - 1, 2):
        # The first item in the pair is a <p> which contains a <span> whose
        # innerText is the day of the week.
        dotw_raw = data[i]
        dotw = dotw_raw.span.text.strip()

        # The second item is a <table> containing the activity data.
        activities_raw = data[i + 1]
        module_data[dotw] = parse_activity_data(activities_raw)

    return module_data


def get_header_data(table):
    # This <table> had a bunch of <tr>s. The data we want is in the last
    # one.

    data = {}

    # • We go through tbody and only get the direct children because if we
    #   search for <tr>s recursively it will be a nightmare.
    # • Because for some reason the direct children <tr>s contain <table>s
    #   which themselves contain <tr>s.
    rows = table.tbody.find_all("tr", recursive=False)

    # Each of the pieces of text we want are in a <b> element
    bolds = rows[-1].find_all("b")

    for b in bolds:
        text = b.text.strip()
        key, value = text.split(": ", 1)
        data[key] = value

    return data


def scrape_raw_timetable_data(driver):
    """
    Scrapes the timetable data displayed on the page which `get_timetable_page`
    already navigated to.
    """

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # • We can get the data we need by iterating over the direct children
    #   of document.body
    # • The pattern in which each module's data is found is like so:
    #   • One <table> containing the "Module:", "Dept:", and "Weeks:" data
    #   • One <p> and one <table> for each day of the week (so 14 total)
    #   • One <table> containing random stuff we don't care about (e.g. the
    #     "Print Timetable" link)
    # • So each module has 16 elements directly under document.body that we
    #   can scrape the data from.

    body = soup.find("body")

    # These are the direct children of document.body.
    # If you simply iterate over 'body' it gets all the non-direct descendants
    # which we don't want in this scenario.
    children = body.find_all(recursive=False)

    timetable_data = []

    for i in range(0, len(children), 16):
        raw_module_data = children[i : i + 16]

        raw_header = raw_module_data[0]
        raw_activity_data = raw_module_data[1:15]
        raw_footer = raw_module_data[15]

        header_data = get_header_data(raw_header)
        module_data = parse_raw_module_data(raw_activity_data)

        timetable_data.append(header_data | module_data)

    return timetable_data


def main():
    driver = get_driver()
    # module_params = get_module_params(driver)
    # pp.pprint(module_params)

    # fmt: off
    get_timetable_page(driver, {
        'days': [ '1-7' ],
        'periods': [ '1-56' ],
        'weeks': [ '38', '25', '51', '12', '47', '21', '34', '8', '30', '43', '17', '4', '39', '26', '52', '13', '48', '22', '35', '9', '31', '44', '18', '5', '40', '27', '14', '1', '49', '23', '36', '10', '32', '45', '19', '6', '41', '28', '15', '2', '50', '24', '37', '11', '33', '46', '20', '7', '42', '29', '16', '3' ],
        'style': [ 'textspreadsheet' ],
        'identifier': [
            'COMP3012',
            'COMP3567',
            'COMP3587',
            'COMP3617',
            'COMP3647',
            'COMP3687',
            'COMP3717',
            'CFLS1G21'
        ]
    })
    # fmt: on

    pp.pprint(scrape_raw_timetable_data(driver))

    driver.quit()


if __name__ == "__main__":
    main()
