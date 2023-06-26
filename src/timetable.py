from pprint import PrettyPrinter

from selenium.webdriver.common.by import By

pp = PrettyPrinter(indent=4)

from utils import (
    get_driver,
    login_to_page_with_url_auth,
)

MODULE_TIMETABLE_URL = "https://timetable.dur.ac.uk/module.htm"


def main():
    driver = get_driver()

    login_to_page_with_url_auth(driver, MODULE_TIMETABLE_URL)

    param_fields = {}

    # The different selection options are stored in <select> elements, each
    # of which has multiple <option> elements which store the user-facing
    # keys and values of the available parameters.

    selects = driver.find_elements(By.TAG_NAME, "select")
    for select in selects:
        # The internal (i.e. not user-facing) name of the <select>.
        # It does give some insight into how the <option>'s are used,
        # but ideally we want to get the label for this <select>.
        name = select.get_attribute("name")

        subfield_params = {}

        options = select.find_elements(By.TAG_NAME, "option")
        for option in options:
            # The <option> element has two values that we care about.
            # The first is its "value" attribute which stores the value that
            # the server will recognise.
            # The second is the innerText value, which is what the user sees.

            key = option.text
            value = option.get_attribute("value")

            subfield_params[key] = value
        param_fields[name] = subfield_params

    return param_fields


if __name__ == "__main__":
    main()
