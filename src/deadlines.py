import os
import time
import csv
import re
from icalendar import Calendar, Event
from datetime import datetime, time, timedelta

strptime = datetime.strptime
combine = datetime.combine

from pprint import PrettyPrinter
from utils import get_driver, login_to_page
from selenium.webdriver.common.by import By

URL = "https://durhamuniversity.sharepoint.com/teams/ComputerScienceUndergraduateCommunity/Lists/Assessment%20schedule%20202324/CS%20Level%201%20deadlines%20202324.aspx?viewid=5ebe17c1%2D9d11%2D4f47%2Db5c7%2D5ebf51debd84"
DOWNLOADS = "/Users/henrybrent/Downloads"

FREE = "TRANSPARENT"
BUSY = "OPAQUE"

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
    deadlines = []
    with open(csv_file_path, "r") as f:
        reader = csv.reader(f)

        col_names = reader.__next__()

        for row in reader:
            deadline = {}

            for col_name, value in zip(col_names, row):
                deadline[col_name] = value

            deadlines.append(deadline)

    # Then, we clean the data for use later in the ICS file
    for deadline in deadlines:
        coursework_title = deadline["Coursework Title"]
        coursework_credits = deadline["Coursework credits"]
        coursework_weighting = deadline["Coursework weighting"]
        estimated_hours = deadline["Estimated hours"]
        feedback_to_students = deadline["Feedback to Students"]
        item = deadline["Item"]
        lecturer = deadline["Lecturer"]
        module_credits = deadline["Module Credits"]
        module_title = deadline["Module Title"]
        release_date = deadline["Release Date"]
        submission_date = deadline["Submission Date"]
        submission_method = deadline["Submission Method"]
        submission_time = deadline["Submission Time"]
        title = deadline["Title"]  # e.g. 'COMP3467'

        # The "Title" value is actually the module code (e.g. 'COMP3467').
        # So it makes sense to change the key name to "Module Code".
        del deadline["Title"]
        deadline["Module Code"] = title

        # Add a new "Title" value, which will be the title of each event.
        # Example: 'COMP3012: "Literature Survey and Project Plan"'
        deadline["_title"] = f'{title}: "{coursework_title}"'

        # Convert "Release Date" into a 'datetime.date' object. As of the
        # time of writing this code, there is no time associated with the
        # release. So it can just be a date.
        deadline["_release_date"] = strptime(release_date, "%d/%m/%Y").date()
        deadline["Release Date"] = deadline["_release_date"].isoformat()

        # Combine "Submission Date" and "Submission Time" into one value;
        # "Submission".
        try:
            # This will work if the submission time is in the format HH:MM
            # Example: "14:00"
            submission_time = datetime.strptime(submission_time, "%H:%M").time()
        except:
            # This part will be reached if the time is something like
            # "11:00:00 am"
            submission_time = datetime.strptime(submission_time, "%I:%M:%S %p").time()

        submission_date = strptime(submission_date, "%d/%m/%Y").date()

        deadline["_submission_time"] = submission_time
        deadline["_submission_date"] = submission_date

        _submission = combine(submission_date, submission_time)

        submission_time = submission_time.strftime("%H:%M")
        submission_date = submission_date.isoformat()

        deadline["Submission Time"] = submission_time
        deadline["Submission Date"] = submission_date
        deadline["_submission"] = _submission

        # Convert "Feedback to Students" into a 'datetime.date' object. As of the
        # time of writing this code, there is no time associated with the
        # release. So it can just be a date.

        deadline["_feedback_to_students"] = strptime(
            feedback_to_students, "%d/%m/%Y"
        ).date()
        deadline["Feedback to Students"] = deadline["_feedback_to_students"].isoformat()

        # Remove anything in parentheses from "Module Title", as it's
        # information that's included in "Coursework Title"
        deadline["Module Title"] = re.sub(r" \(.+\)", "", module_title)

    # Create ICS file
    cal = Calendar()

    for entry in deadlines:
        # Each deadline will have the following events:
        # - Release
        # - Submission
        # - Feedback

        release = Event()
        submission = Event()
        feedback = Event()

        # Add SUMMARY
        _title = entry["_title"]
        release.add("summary", f"Release: {_title}")
        submission.add("summary", f"Submission: {_title}")
        feedback.add("summary", f"Feedback: {_title}")

        # Create a description
        description = "Deadline details:\n\n"
        for key, value in entry.items():
            # Ignore the private variables
            if key.startswith("_"):
                continue
            description += f"{key}: {value}\n"
        # Get rid of the extra newline at the end
        description = description[:-1]

        release.add("description", description)
        submission.add("description", description)
        feedback.add("description", description)

        # Add DTSTART and DTEND
        # Putting the same start and end time makes it an "instant" event
        _submission = entry["_submission"]
        submission.add("dtstart", _submission)
        submission.add("dtend", _submission)

        # I'm making the Release event an all-day event since there is no
        # time specified.
        release_dtstart = combine(entry["_release_date"], time.min)
        release_dtend = release_dtstart + timedelta(days=1)
        release.add("dtstart", release_dtstart)
        release.add("dtend", release_dtend)

        # Add TRANSP (to indicate whether the events are free/busy)
        release.add("transp", FREE)
        submission.add("transp", FREE)
        feedback.add("transp", FREE)

        cal.add_component(release)
        cal.add_component(submission)
        cal.add_component(feedback)


if __name__ == "__main__":
    main()
