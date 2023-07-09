import os
import time
import json

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd


# The chromedriver executable should be located at root of project.
_this_directory = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_this_directory, os.pardir))
CHROMEDRIVER_PATH = os.path.join(_project_root, "chromedriver")


def get_driver(options: list[str] = []) -> Chrome:
    """Initialises a new instance of the Chrome webdriver and returns it."""
    # Create options object.
    # Allows you to configure options (who would have thought)
    # e.g. whether chrome should run headlessly (is that a word?).
    # options.add_argument("--headless")
    driver_opts = Options()
    for option in options:
        driver_opts.add_argument(option)

    driver = Chrome(executable_path=CHROMEDRIVER_PATH, options=driver_opts)

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


def login_to_page_with_MFA(driver: Chrome, url: str) -> None:
    """
    Gets the `driver` past the login stage to get to the `url` provided.
    """
    driver.get(url)
    dotenv = parse_dotenv()

    # If there's a username and password in a .env file at the root of the
    # project, use those to autofill the login fields and submit them.
    if bool(dotenv):
        USERNAME = dotenv["USERNAME"]
        PASSWORD = dotenv["PASSWORD"]

        await_element(driver, 'input[type="email"]').send_keys(USERNAME)
        await_element(driver, 'input[type="submit"]').click()
        time.sleep(1)
        await_element(driver, 'input[type="password"]').send_keys(PASSWORD)
        time.sleep(1)
        driver.execute_script("document.forms[0].submit()")

    wait_until_reached(driver, url)


def add_auth(url: str, username: str, password: str) -> str:
    # Replace the email extension thingy (if it's there).
    username = username.replace("@durham.ac.uk", "")
    # Return the original URL with "<username>:<password>@" put in after the
    # "http(s)://" part. That's how we provide the basic auth needed to access
    # certain pages.
    return url.replace("://", f"://{username}:{password}@")


def get_url_with_auth(url: str) -> str:
    """
    1. Gets the username and password from `.env`
    2. Adds them to the provided url
    3. Returns the modified url
    """
    dotenv = parse_dotenv()

    if not bool(dotenv):
        raise NameError("No .env file found")

    USERNAME = dotenv["USERNAME"]
    PASSWORD = dotenv["PASSWORD"]

    return add_auth(url, USERNAME, PASSWORD)


def login_to_page_with_url_auth(driver: Chrome, url: str) -> None:
    """
    Gets the `driver` past the login stage to get to the `url` provided.
    """
    url = get_url_with_auth(url)
    wait_until_reached(driver, url)


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


def get_parent(element):
    """
    Given a `element` (i.e. a Web Element), this function returns the parent.
    """
    return element.find_element(By.XPATH, "./..")


def get_previous_sibling(element):
    """
    Given an `element`, this function returns the previous sibling.

    It does this by finding the parent, then iterating through the parent's
    children til it hits the element passed in as a parameter, then it
    returns the element before that one.
    """
    parent = get_parent(element)
    children = parent.find_elements(By.XPATH, "./child::*")

    for index, child in enumerate(children):
        if element != child:
            continue

        # If the 'element' provided in the params is the first child of its
        # parent, return None.
        if index == 0:
            return None

        # Else, return the child before this one.
        return children[index - 1]

    return None
