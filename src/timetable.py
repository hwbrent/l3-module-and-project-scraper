from pprint import PrettyPrinter

from selenium.webdriver.common.by import By

pp = PrettyPrinter(indent=4)

from utils import (
    get_driver,
    login_to_page_with_url_auth,
    get_parent,
    get_previous_sibling,
)

MODULE_TIMETABLE_URL = "https://timetable.dur.ac.uk/module.htm"


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

    for _, option_values in choices.items():
        for option_value in option_values:
            # You can't programmatically set the attribute of a WebElement
            # with Selenium, so you have to use JavaScript to do it instead
            driver.execute_script(
                f'document.querySelector(`[value="{option_value}"]`).selected = true;'
            )

    # Click the "submit" button
    view_timetable_button = driver.find_element(
        By.CSS_SELECTOR, 'input[value="View Timetable"]'
    )
    view_timetable_button.click()


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


if __name__ == "__main__":
    main()
