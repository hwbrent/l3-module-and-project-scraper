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


def find_el_by_inner_text(driver, text: str):
    """
    Finds and returns an element containing `text`.

    See https://stackoverflow.com/a/18701085/17406886.
    """
    return driver.find_element(
        By.XPATH, f"//body//*[not(self::script) and contains(text(), '{text}')]"
    )


def get_el_parent(element):
    """
    Given an `element`, returns the parent of that element.
    """
    return element.find_element(By.XPATH, "..")
