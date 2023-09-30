from utils import get_driver, login_to_page
from selenium.webdriver.common.by import By

URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/Lists/Assessment%20schedule%20202324/CS%20Level%201%20deadlines%20202324.aspx?viewid=5ebe17c1%2D9d11%2D4f47%2Db5c7%2D5ebf51debd84"


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


if __name__ == "__main__":
    main()
