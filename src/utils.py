import os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


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
