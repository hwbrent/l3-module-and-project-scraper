import time
from pprint import PrettyPrinter

from selenium.webdriver.common.by import By

from utils import (
    get_driver,
    wait_until_reached,
    await_element,
    parse_dotenv,
    find_el_by_inner_text,
    get_el_parent,
)

pp = PrettyPrinter(indent=4)

MODULES_SITE_URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/SitePages/Level-3-M.aspx"


def get_module_page_urls(driver):
    assert driver.current_url == MODULES_SITE_URL

    # There is a bullet-point list near the top of the page of all the
    # modules offered. We want to get that list. It doesn't have an ID,
    # so the best way is probably to find the <p> element above it, which
    # contains a chunk of text. We can search for the phrase "Below are
    # links to outlines for all level 3 Computer Science modules available
    # in 2023-24", then get the parent of that element, then find the <ul>
    # within that parent.

    p_above_ul = find_el_by_inner_text(
        driver,
        "Below are links to outlines for all level 3 Computer Science modules available in 2023-24",
    )

    p_parent = get_el_parent(p_above_ul)
    lis = p_parent.find_elements(By.TAG_NAME, "li")

    module_names_and_urls = {}

    for li in lis:
        # Each <li> has a descendant <a>. This <a> has an attribute 'href'
        # which obviously tells you on which page the module information
        # can be found.

        a = li.find_element(By.XPATH, ".//a")

        # This is the name of the module. It'll look something like this:
        # "COMP3567 Multimedia and Game Development" (without the quotation
        # marks obviously).
        name = a.get_attribute("innerText")

        # Some module names include the number of credits, e.g. "COMP3591
        # Project Preparation (20 Credits)". Obviously we don't want the
        # part mentioning the credits. Doing [:-13] gets rid of the part in
        # brackets and the whitespace in front of the opening bracket.
        if "0 Credits)" in name:
            name = name[:-13]

        href = a.get_attribute("href")

        module_names_and_urls[name] = href

    return module_names_and_urls


def scrape_raw_data():
    driver = get_driver()
    driver.get(MODULES_SITE_URL)

    # Even though we tried to navigate to the modules webpage, we will have
    # been redirected to the microsoft online login page. At this point, it's
    # easier to just wait until the user manually logs in than try any fancy
    # stuff.

    dotenv = parse_dotenv()

    if bool(dotenv):
        USERNAME = dotenv["USERNAME"]
        PASSWORD = dotenv["PASSWORD"]

        await_element(driver, 'input[type="email"]').send_keys(USERNAME)
        await_element(driver, 'input[type="submit"]').click()
        time.sleep(1)
        await_element(driver, 'input[type="password"]').send_keys(PASSWORD)
        time.sleep(1)
        driver.execute_script("document.forms[0].submit()")

    wait_until_reached(driver, MODULES_SITE_URL)
    time.sleep(1)

    pp.pprint(get_module_page_urls(driver))


def main():
    scrape_raw_data()


if __name__ == "__main__":
    main()
