from utils import (
    get_driver,
    login_to_page,
    write_to_json,
    write_to_excel,
    write_to_markdown,
)

PROJECTS_SITE_URL = "https://cssystems.awh.durham.ac.uk/password/projects/student/"


# ------------------------------


def scrape_raw_data(driver) -> list[dict]:
    login_to_page(driver, PROJECTS_SITE_URL)

    # This will contain the `dict`s containg each project's info.
    aggregate_data = []

    # • I was poking around with the browser devtools and noticed that
    #   get the project data, calls were being made to 'Registers.php'.
    # • I thought "what if I can make the same calls myself", so I tried
    #   it in the browser console and it worked.
    # • So I wondered "can I do this with Selenium?", so I gave that a go
    #   too, and it worked!
    # • So to me it made sense to make those same calls here rather than
    #   have to go to the extra effort of scraping the data from the DOM.

    projects = driver.execute_script(
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

    for project in projects:
        # `project` is a `dict` which looks like something like this:
        # {
        #     "title": "Connectivity of interval temporal networks",
        #     "theme": 162,
        #     "staff": "jxfn92",
        #     "initials": "EA",
        #     "forename": "Eleni",
        #     "surname": "Akrida"
        # }

        # • This server call returns the more in-depth data that you see
        #   in the table at the top of the page after you click the project
        #   title.
        # • The request is for a single project's data, but for some reason
        #   the data (a `dict`) is returned within a `list`. Hence the `[0]`.
        # • An example of the data returned is this:
        # [{
        #     "description": """An interval temporal network is a network whose
        #                       edges are active for one or more time intervals
        #                       and inactive the rest of the time. Work has
        #                       been done previously on instantaneous connectivity
        #                       of interval temporal networks, where the network
        #                       is considered to be connected during a period
        #                       of time [x,y], if it is connected for all time
        #                       instances within the continuous time interval
        #                       [x,y]. This project will look at the
        #                       implementation of existing and possible
        #                       development of new approaches to preserve
        #                       connectivity of an interval temporal network
        #                       over time (by maintaining a 'bank' of extra
        #                       edges, available during certain time intervals,
        #                       which can reconnect the network in case it
        #                       becomes disconnected).""",
        #     "interview": 0,
        #     "keywords": "temporal graph, graph connectivity, algorithm",
        #     "l3": 1,
        #     "l4": 1,
        #     "maxStudents": "0",
        #     "outcomes": """Implementation and evaluation of existing algorithms
        #                    with possible development of new approaches.""",
        #     "skills": """An interest and background knowledge
        #                  in graph theory and graph algorithms """,
        #     "themeID": 162,
        #     "title": "Connectivity of interval temporal networks",
        #     "url": "https://www.worldscientific.com/doi/pdf/10.1142/S0129626419500099",
        # }]
        in_depth_info = driver.execute_script(
            f"""
            return await $.ajax({{
                type: "GET",
                dataType: "json",
                url: "Registers.php",
                data: {{
                    "query": "oneProject",
                    "theme": {project["theme"]}
                }}
            }})
            """
        )[0]

        # • Here, we merge the surface-level from the first initial
        #   'allProjects' request with the more in-depth data from the
        #   'oneProject' call into one `dict`.
        new_dict = project | in_depth_info

        aggregate_data.append(new_dict)

    return aggregate_data


def get_project_type(l3_raw: int, l4_raw: int) -> str:
    """
    Parses the `l3` and `l4` values from the server and turns them into a
    user-facing string.

    The server's response object has properties `l3` and `l4`. As far as I
    can tell, if the project is available at that level, the value will be
    `1`, else `0`.
    """
    l3_yes_no = "Yes" if bool(l3_raw) else "No"
    l4_yes_no = "Yes" if bool(l4_raw) else "No"
    return f"CS Level 3: {l3_yes_no}, CS Level 4: {l4_yes_no}"


def get_interview_required(interview: int) -> str:
    """
    Parses the `interview` value from the server and turns it into a
    user-facing string.

    The server's response object has a property `interview`. As far as I
    can tell, if the project requires an interview, the value will be
    `1`, else `0`.
    """
    return "Yes" if bool(interview) else "No"


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
            "Project Type":         get_project_type(entry['l3'], entry['l4']),
            "Keywords":             entry["keywords"],
            "Interview Required":   get_interview_required(entry["interview"])
        })
        # fmt: on

    return all_reformatted


# ------------------------------


def main():
    driver = get_driver()
    raw = scrape_raw_data(driver)
    driver.quit()

    formatted = format_raw_data(raw)

    write_to_json(raw, "projects")
    # We need to pass in the raw and formatted data to write_to_markdown
    # so that it has access to the full staff member names in 'raw' and
    # thus can create headers with the staff member names.
    write_to_markdown({"raw": raw, "formatted": formatted}, "projects")
    write_to_excel(formatted, "projects")


if __name__ == "__main__":
    main()
