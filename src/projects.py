import time
import json
import string
from pprint import PrettyPrinter

from bs4 import BeautifulSoup

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


def sanitise_for_markdown(raw_value: str) -> str:
    """
    This function accepts the value corresponding to one of the keys in a
    project's `dict` and reformats it so that it works in markdown.

    As part of `write_to_markdown` we want to be able to construct a table
    for each project like you see on the original webpage when you click the
    unexpanded project title. However, the values that the server returns
    include things lile newlines which, if left, cause the formatting of
    the tables we generate to break. Therefore we need to sanitise the string
    for use in markdown.
    """

    # First, strip any whitespace off the ends
    formatted_text = raw_value.strip()

    # Then handle any HTML elements. If it's an <a> we replace it with its
    # 'href', otherwise we replace it with its inner text. Credit goes to
    # ChatGPT for this <3
    soup = BeautifulSoup(formatted_text, "html.parser")
    for element in soup.find_all(True):
        if element.name == "a":
            href = element.get("href")
            if href:
                element.string = href
            else:
                element.extract()
        else:
            element.unwrap()
    formatted_text = soup.get_text()

    # Convert special characters to Markdown equivalents
    formatted_text = formatted_text.replace(
        "\n", "<br>"
    )  # Add two spaces at the end for line break in Markdown
    formatted_text = formatted_text.replace("\r", "")
    formatted_text = formatted_text.replace(
        "\t", "    "
    )  # Add four spaces for tab in Markdown

    # Vertical bars are used in Markdown to format tables, so if the text
    # to go into a table cell contains a vertical bar, it needs to be
    # escaped to stop it breaking the whole table.
    formatted_text = formatted_text.replace("|", "\|")

    return formatted_text


def format_project_type_for_markdown(project_type: str) -> str:
    """
    Given the Project Type data for a project, this function reformats it
    by putting it on two lines and replacing Yes/No with the equivalent emoji.

    For example:

    CS Level 3: Yes, CS Level 4: No

    becomes

    CS Level 3: ✅
    CS Level 4: ❌
    """

    CHECKMARK = "\u2705"
    CROSS = "\u274C"

    # Replace the Yes/No text with their respective emojis.
    project_type = project_type.replace("Yes", CHECKMARK)
    project_type = project_type.replace("No", CROSS)

    # Add a newline to put the CS Level 3 and CS Level 4 values on their
    # own lines for readability.
    project_type = project_type.replace(", CS Level 4:", "\nCS Level 4:")

    return project_type


def get_markdown_header_id(text: str) -> str:
    """
    Given the name of a project, this function generates the id for that
    project's entry.

    For example:
    AA-6: Can surgery revitalize the eyes?
    becomes
    #aa-6-can-surgery-revitalize-the-eyes

    See: https://stackoverflow.com/a/38507669/17406886.
    """

    # Remove any leading/trailing whitespace.
    text = text.strip()

    # Make everything lowercase.
    text = text.lower()

    # Remove any punctuation which isn't a hyphen.
    # (Thanks ChatGPT for this solution <3)
    punctuation = string.punctuation.replace("-", "")
    translator = str.maketrans("", "", punctuation)
    text = text.translate(translator)

    # Replace spaces with hyphens
    text = text.replace(" ", "-")

    return text


def write_to_markdown(data: list[dict], file_name: str) -> None:
    contents = []
    contents.append("## Contents\n")

    tables = []

    for entry in data:
        # First off, we can slightly reformat a few items in the entry to
        # make them look a bit nicer in the resulting markdown.
        entry["Project Type"] = format_project_type_for_markdown(entry["Project Type"])

        # For some reason there was a rogue title that had a newline in it
        # which stopped the link in the Contents section from working. This
        # fixes that.
        entry["Project Theme/Title"] = (
            entry["Project Theme/Title"].strip().replace("\n", "")
        )

        # We need to generate an entry for the table of contents at the top
        # of the file.
        # The idea is to have a bullet point with the title of the project
        # and a link to the table further down in the document.

        title = entry["Project Theme/Title"]
        link = get_markdown_header_id(title)

        # This is the raw markdown that we will put in the file.
        md_bullet_point = f" * [{title}](#{link})"
        contents.append(md_bullet_point)

        # Now we generate the markdown table corresponding to the current
        # project.
        table = []

        # First, we add a header above the table so that we can link to this
        # specific table.
        table.append(f"### {title}\n")

        # Now, we generate the actual table.

        # There's no point in adding the title to the table seeing as it's
        # in the header above the table. So we skip the first key/value pair
        # in the entry.
        items = list(entry.items())[1:]

        for index, (key, value) in enumerate(items):
            value = sanitise_for_markdown(value)

            if index == 0:
                # By default, the text in the first row of the table is bold.
                # In this case we don't want that, so the easiest way to
                # override it is to set the font-weight CSS property on a
                # <span> which contains the text.
                # See: https://stackoverflow.com/a/28654491/17406886.
                md_row = f"| <span style='font-weight:normal'>{key}</span> | <span style='font-weight:normal'>{value}</span> |"
                table.append(md_row)

                # After the first row, we need to add the weird row where the
                # cells only contain dashes.
                table.append("| :- | :- |")
                continue

            md_row = f"| {key} | {value} |"
            table.append(md_row)

        table = "\n".join(table)
        tables.append(table)

    contents = "\n".join(contents)
    tables = "\n\n".join(tables)

    file = contents + "\n<hr>\n\n" + tables

    with open(
        "/Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/projects.md",
        "w",
    ) as f:
        f.write(file)


def main():
    # raw = scrape_raw_data()

    with open(
        "/Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/projects.json",
        "r",
    ) as f:
        raw = json.load(f)

    formatted = format_raw_data(raw)

    write_to_markdown(formatted, "projects")

    # write_to_json(raw, "projects")
    # write_to_excel(formatted, "projects")


if __name__ == "__main__":
    main()
