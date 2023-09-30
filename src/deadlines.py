from utils import get_driver, login_to_page

URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/Lists/Assessment%20schedule%20202324/CS%20Level%201%20deadlines%20202324.aspx?viewid=5ebe17c1%2D9d11%2D4f47%2Db5c7%2D5ebf51debd84"


def main():
    driver = get_driver()
    login_to_page(driver, URL)


if __name__ == "__main__":
    main()
