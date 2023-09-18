import requests
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

URL = "https://www.durham.ac.uk/academic-dates/"


def scrape_term_dates():
    response = requests.get(URL)
    pp.pprint(response.text)
    pass


def main():
    term_dates = scrape_term_dates()


if __name__ == "__main__":
    main()
