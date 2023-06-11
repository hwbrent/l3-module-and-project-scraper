### `chromedriver`
- Can (and should) be installed from https://chromedriver.chromium.org/downloads
- Needs to be placed at root of directory
- If you run `projects.py` and get an error like so in the console:
> selenium.common.exceptions.WebDriverException: Message: Service /Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/chromedriver unexpectedly exited. Status code was: -9
- ... be wary of errors from your machine to do with not trusting executables downloaded from the internet. You will need to allow `chromedriver` to be executed for this code to work