import utils

URL = "https://mytimetable.durham.ac.uk/weekly/activities"


def main():
    driver = utils.get_driver()
    driver.quit()


if __name__ == "__main__":
    main()
