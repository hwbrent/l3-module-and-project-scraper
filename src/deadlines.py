import os
import time
import csv
from pprint import PrettyPrinter
from utils import get_driver, login_to_page
from selenium.webdriver.common.by import By

URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/Lists/Assessment%20schedule%20202324/CS%20Level%201%20deadlines%20202324.aspx?viewid=5ebe17c1%2D9d11%2D4f47%2Db5c7%2D5ebf51debd84"
DOWNLOADS = "/Users/henrybrent/Downloads"


def main():
    driver = get_driver()
    login_to_page(driver, URL)

    # We need to click the "Export" button to get the "Export to CSV"
    # button to appear
    export_button = driver.find_element(By.CSS_SELECTOR, 'button[name="Export"]')
    export_button.click()

    # Trigger the downloading of the CSV
    export_to_csv_button = driver.find_element(
        By.CSS_SELECTOR, 'button[name="Export to CSV"]'
    )
    export_to_csv_button.click()

    # Wait for the download to complete
    csv_file_path = None
    timeout = 60  # Adjust this timeout as needed
    while timeout > 0:
        # Check if the file exists in the download directory
        files = os.listdir(DOWNLOADS)
        if files:
            files = os.listdir(DOWNLOADS)
            paths = [os.path.join(DOWNLOADS, basename) for basename in files]
            most_recent = max(paths, key=os.path.getctime)
            if most_recent.endswith(".csv"):
                csv_file_path = most_recent
                break
        time.sleep(1)
        timeout -= 1

    # If the csv can't be found in downloads, that means it wasn't downloaded
    # within the timeout period. So there was probably some kind of issue. So
    # quit
    if csv_file_path is None:
        print("No downloaded CSV file was found. Exiting...")
        return

    # First, we get the deadline data exactly as it's represented in the csv
    raw_deadlines = []
    with open(csv_file_path, "r") as f:
        reader = csv.reader(f)

        col_names = reader.__next__()

        for row in reader:
            deadline = {}

            for col_name, value in zip(col_names, row):
                deadline[col_name] = value

            raw_deadlines.append(deadline)


if __name__ == "__main__":
    main()
