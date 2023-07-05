### `chromedriver`
- Can (and should) be installed from https://chromedriver.chromium.org/downloads
- Needs to be placed at root of directory
- If you run `projects.py` and get an error like so in the console:
> selenium.common.exceptions.WebDriverException: Message: Service /Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/chromedriver unexpectedly exited. Status code was: -9
- ... be wary of errors from your machine to do with not trusting executables downloaded from the internet. You will need to allow `chromedriver` to be executed for this code to work

### Bugs
<details>
<summary>Click to see a dropdown of bugs/errors encountered and their fixes</summary>

```bash
Traceback (most recent call last):
  File "/Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/src/projects.py", line 211, in <module>
    main()
  File "/Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/src/projects.py", line 196, in main
    driver = get_driver()
  File "/Users/henrybrent/Documents/GitHub/l3-module-and-project-scraper/src/utils.py", line 31, in get_driver
    driver = Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
  File "/Users/henrybrent/opt/anaconda3/lib/python3.9/site-packages/selenium/webdriver/chrome/webdriver.py", line 76, in __init__
    RemoteWebDriver.__init__(
  File "/Users/henrybrent/opt/anaconda3/lib/python3.9/site-packages/selenium/webdriver/remote/webdriver.py", line 157, in __init__
    self.start_session(capabilities, browser_profile)
  File "/Users/henrybrent/opt/anaconda3/lib/python3.9/site-packages/selenium/webdriver/remote/webdriver.py", line 252, in start_session
    response = self.execute(Command.NEW_SESSION, parameters)
  File "/Users/henrybrent/opt/anaconda3/lib/python3.9/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/Users/henrybrent/opt/anaconda3/lib/python3.9/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary
```
- Turns out this was caused by not having Chrome installed
- I use Firefox for browsing the web, so recently I deleted Chrome to free up some space on my hard disc. Didn't occur to me that this would cause an issue with Selenium
- This [StackOverflow comment](https://stackoverflow.com/a/65664901/17406886) is what helped me realise

</details>