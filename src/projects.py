import time
from pprint import PrettyPrinter

from utils import get_driver, wait_until_reached, await_element

from selenium.webdriver.common.by import By

pp = PrettyPrinter(indent=4)

PROJECTS_SITE_URL = "https://cssystems.awh.durham.ac.uk/password/projects/student/"


def parse_unclicked_project_row(row, staff_proposer):
    # This is the HTML id attribute of the <tr>.
    id = row.get_attribute("id")

    # Each <tr> contains a singular <td>. The text inside this <td> is the
    # data that we want to scrape.
    row_text = row.find_element(By.TAG_NAME, "td").text
    print(id, row_text)

    # row_text should be something like "Theme EA-1: Connectivity of interval
    # temporal networks".

    # We set maxsplit as 1 because there are some project names that include
    # ": " in them, e.g.:
    # "No Such Thing as Normal: Anomaly Detection with Anomaly Class Selection"
    project_title = row_text.replace("Theme: ", "")

    return {
        "id": id,
        "project_title": project_title,
        "staff_proposer": staff_proposer,
    }


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

    staff_proposer_tables = driver.find_elements(
        By.CSS_SELECTOR, "#projectTitles table"
    )

    for professor_table in staff_proposer_tables:
        # Each of these tables is the table showing
        # e.g.:
        # | Staff Proposer: Eleni Akrida                                                                              |
        # | Theme EA-1: Connectivity of interval temporal networks                                                    |
        # | Theme EA-2: Approximation algorithms for the minimum temporal vertex cover problem                        |
        # | Theme EA-3: Exact and approximation algorithms for exploration of temporal stars and other dynamic graphs |
        # | Theme EA-4: Binary search on graphs                                                                       |
        # | Theme EA-5: Path and reachability problems in temporal graphs                                             |

        # Example of what the table element looks like:
        """
        <table>
            <tbody>
                <tr><td>Staff Proposer: Eleni Akrida</td></tr>
                <tr id="EA-1"><td>Theme EA-1: Connectivity of interval temporal networks</td></tr>
                <tr id="EA-2"><td>Theme EA-2: Approximation algorithms for the minimum temporal vertex cover problem</td></tr>
                <tr id="EA-3"><td>Theme EA-3: Exact and approximation algorithms for exploration of temporal stars and other dynamic graphs</td></tr>
                <tr id="EA-4"><td>Theme EA-4: Binary search on graphs</td></tr>
                <tr id="EA-5"><td>Theme EA-5: Path and reachability problems in temporal graphs</td></tr>
            </tbody>
        </table>
        """

        rows = professor_table.find_elements(By.TAG_NAME, "tr")

        # The first row of each table contains the name of the staff proposer.
        # We can just grab it out of there once and reuse it for each project
        # row in this table. The text will be something like
        # "Staff Proposer: Eleni Akrida".
        staff_proposer_name = (
            rows[0].find_element(By.TAG_NAME, "td").text.replace("Staff Proposer: ", "")
        )

        for row in rows[1:]:
            initial_project_data = parse_unclicked_project_row(row, staff_proposer_name)
            pp.pprint(initial_project_data)
            print()

            # At this point, we have the data of the unclicked row. Which
            # essentially means we only have the project title. Now we
            # need to click the row and parse the table at the top of the
            # page.

    driver.quit()


if __name__ == "__main__":
    main()
