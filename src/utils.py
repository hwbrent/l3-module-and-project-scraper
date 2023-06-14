import os
import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
