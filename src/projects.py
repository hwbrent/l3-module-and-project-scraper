from utils import get_driver, wait_until_reached, await_element
import time

from selenium.webdriver.common.by import By


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
        print(professor_table)
        # print()
        # print()

    driver.quit()


if __name__ == "__main__":
    main()
