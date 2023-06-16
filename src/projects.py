import time
import json
from pprint import PrettyPrinter

from utils import (
    get_driver,
    wait_until_reached,
    await_element,
    write_to_json,
    parse_dotenv,
    write_to_excel,
)

pp = PrettyPrinter(indent=4)

PROJECTS_SITE_URL = "https://cssystems.awh.durham.ac.uk/password/projects/student/"


def scrape_raw_data():
    driver = get_driver()
    driver.get(PROJECTS_SITE_URL)

    # Even though we tried to navigate to the projects webpage, we will have
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

    driver.quit()

    return aggregate_data


def format_raw_data(data: list[dict]) -> list[dict]:
    """Receives a `list` of `dict`s representing the server information, and returns a `list` of `dict`s representing the information seen in the DOM."""
    all_reformatted = []

    # The showTitles function does this:
    """
    var staffID = "";
    var localThemeID = 0;

    for (i = 1; i < (data.length) + 1; i++) {
        if (staffID == "") {
            staffID = data[i-1]['staff']
            var forename = data[i-1]['forename'];
            var surname = data[i-1]['surname'];
            text.innerHTML = "Staff Proposer: " + forename + " " + surname;
        } else if (staffID != data[i-1]['staff']) {
            staffID = data[i-1]['staff']
            var forename = data[i-1]['forename'];
            var surname = data[i-1]['surname'];
            text.innerHTML = "Staff Proposer: " + forename + " " + surname;
            localThemeID = 0;
        }
        row.name = data[i-1]['theme'];
        localThemeID++;
        var themeNumber = data[i-1]['initials'] + "-" + localThemeID;
        row.id = themeNumber;
        text.innerHTML = "Theme " + themeNumber + ": " + data[i-1]['title'];
    }
    """
    # And the getProjectDetails function does this:
    """
    for (i = 0; i < data.length; i++) {
        // Row 0
        title.innerHTML = "Project Theme/Title";
        text.innerHTML = themeNumber + ": " + data[i]['title'];
        // Row 1
        desc.innerHTML = "Description";
        text.innerHTML = data[i]['description'];
        // Row 2
        url.innerHTML = "Reference URLs"
        text.innerHTML = data[i]['url'];
        // Row 3
        out.innerHTML = "Anticipated Outcomes"
        text.innerHTML = data[i]['outcomes'];
        // Row 4
        skills.innerHTML = "Requirements"
        text.innerHTML = data[i]['skills'];
        // Row 5
        max.innerHTML = "Keywords"
        text.innerHTML = data[i]['keywords'];
    """

    # The sub-number of the project.
    # i.e. the number of the project with respect to the other projects
    # offered by this staff member. Professors generally offer multiple
    # projects, so this represents the n-th project that a given member
    # of staff offers.
    localThemeId = 0

    for index, entry in enumerate(data):
        this_staff = entry["staff"]
        prev_staff = data[index - 1]["staff"] if index > 0 else this_staff
        if this_staff != prev_staff:
            localThemeId = 0
        localThemeId += 1

        # AA-7, NBe-2, SSD-3, etc.
        themeNumber = entry["initials"] + "-" + str(localThemeId)

        # fmt: off
        all_reformatted.append({
            "Project Theme/Title":  themeNumber + ": " + entry["title"],
            "Description":          entry["description"],
            "Reference URLs":       entry["url"],
            "Anticipated Outcomes": entry["outcomes"],
            "Requirements":         entry["skills"],
            "Keywords":             entry["keywords"],
        })
        # fmt: on

    return all_reformatted


def main():
    raw = scrape_raw_data()
    write_to_json(raw, "projects")
    formatted = format_raw_data(raw)
    write_to_excel(formatted, "projects")


if __name__ == "__main__":
    main()
