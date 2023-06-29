import os
import time
import json
import string

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

from bs4 import BeautifulSoup


# The chromedriver executable should be located at root of project.
_this_directory = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_this_directory, os.pardir))
CHROMEDRIVER_PATH = os.path.join(_project_root, "chromedriver")


def get_driver() -> Chrome:
    """Initialises a new instance of the Chrome webdriver and returns it."""
    # Create options object.
    # Allows you to configure options (who would have thought)
    # e.g. whether chrome should run headlessly (is that a word?).
    options = Options()
    # options.add_argument("--headless")

    driver = Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    return driver


def await_element(driver, selector, by=By.CSS_SELECTOR, timeout_secs=10) -> None:
    """Waits until an element with selector `selector` appears, and returns it. Waits for `timeout_secs` seconds"""
    wait = WebDriverWait(driver, timeout_secs)
    element = wait.until(EC.presence_of_element_located((by, selector)))
    return element


def wait_until_reached(driver: Chrome, destination_url: str) -> None:
    """Keeps `driver` alive until it reaches the `destination_url`. Used to allow user to log in manually to Durham Uni Outlook account."""
    while driver.current_url != destination_url:
        time.sleep(2)


def write_to_json(data: list, file_name) -> None:
    """Outputs `data` to a JSON file."""
    destination = os.path.join(_project_root, file_name + ".json")
    with open(destination, "w") as f:
        json.dump(data, f, indent=4)


def parse_dotenv() -> dict:
    """Parses a .env file (if it exists) and return the values in a `dict`."""
    dotenv_path = os.path.join(_project_root, ".env")

    if not os.path.exists(dotenv_path):
        return {}

    keys_and_values = {}

    with open(dotenv_path, "r") as f:
        for line in f:
            line = line.strip()

            key_raw, value_raw = line.split("=")

            key = key_raw.strip()
            value = value_raw.strip().replace('"', "")

            keys_and_values[key] = value

    return keys_and_values


def write_to_excel(data: list[dict], file_name: str) -> None:
    """Writes the `data` to a .xlsx document"""
    df = pd.DataFrame.from_dict(data, orient="columns")
    destination = os.path.join(_project_root, file_name + ".xlsx")
    df.to_excel(destination, index=False)


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
