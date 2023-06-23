MODULES_SITE_URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/SitePages/Level-3-M.aspx"

import time
from pprint import PrettyPrinter

from utils import (
    get_driver,
    wait_until_reached,
    await_element,
    parse_dotenv,
)

pp = PrettyPrinter(indent=4)

MODULES_SITE_URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/SitePages/Level-3-M.aspx"


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

    input()


def main():
    scrape_raw_data()


if __name__ == "__main__":
    main()
