import utils

URL = "https://mytimetable.durham.ac.uk/weekly/activities"


def main():
    driver = utils.get_driver()
    utils.login_to_page(driver, URL)

    input()

    driver.quit()


if __name__ == "__main__":
    main()
