import time
from pprint import PrettyPrinter

from utils import get_driver, wait_until_reached, await_element

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

    # This is the list that will contain all the "projects", i.e. all the
    # dictionaries containg information on each project's.
    aggregate_data = []

    # The data returned in this call is akin to the data you see in the
    # unclicked staff proposer tables. It returns a list of dictionaries
    # such as the below
    """
    {
        "title": "Connectivity of interval temporal networks",
        "theme": 162,
        "staff": "jxfn92",
        "initials": "EA",
        "forename": "Eleni",
        "surname": "Akrida"
    }
    """
    all_projects = driver.execute_script(
        """
        return await $.ajax({
            type: "GET",
            dataType: "json",
            url: "Registers.php",
            data: {
                "query": "allProjects"
            }
        })
        """
    )

    for project in all_projects:
        # This is a parameter that is passed to the $.ajax call.
        id = project["theme"]

        # For some reason, even though we're specifying we want the data for
        # one project, it returns a dictionary within a list. Hence the "[0]".
        in_depth_info = driver.execute_script(
            f"""
            return await $.ajax({{
                type: "GET",
                dataType: "json",
                url: "Registers.php",
                data: {{
                    "query": "oneProject",
                    "theme": {id}
                }}
            }})
            """
        )[0]

        # This essentially merges the two dictionaries into one.
        new_dict = project | in_depth_info

        aggregate_data.append(new_dict)

    pp.pprint(aggregate_data)

    driver.quit()


if __name__ == "__main__":
    main()
