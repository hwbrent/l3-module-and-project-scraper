import time
import json
from pprint import PrettyPrinter

from utils import get_driver, wait_until_reached, await_element

from selenium.webdriver.common.by import By

pp = PrettyPrinter(indent=4)

PROJECTS_SITE_URL = "https://cssystems.awh.durham.ac.uk/password/projects/student/"


def main():
    driver = get_driver()
    driver.get(PROJECTS_SITE_URL)

    # Even though we tried to navigate to the projects webpage, we will have
    # been redirected to the microsoft online login page. At this point, it's
    # easier to just wait until the user manually logs in than try any fancy
    # stuff.

    wait_until_reached(driver, PROJECTS_SITE_URL)
    time.sleep(1)

    # For some reason, none of the tables seem to load unless you refresh
    # the page after it first loads.
    driver.refresh()
    time.sleep(1)

    all_projects = driver.execute_script(
        'return await $.ajax ({type: "GET",dataType: "json", url: "Registers.php",data: { "query": "allProjects"}})'
    )

    aggregate_data = []

    for project in all_projects:
        id = project["theme"]
        in_depth_info = driver.execute_script(
            'return await $.ajax ({type: "GET",dataType: "json", url: "Registers.php",data: { "query": "oneProject", "theme":'
            + str(id)
            + "}})"
        )[0]

        new_dict = project | in_depth_info

        aggregate_data.append(new_dict)

    pp.pprint(aggregate_data)

    driver.quit()


if __name__ == "__main__":
    main()
