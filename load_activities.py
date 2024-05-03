import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.by import By
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

def parse_date(date_string):
    formats = ['%m/%d/%y %I:%M %p', '%m/%d/%y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError(f"No valid date format found from {date_string}")

def wait_to_click(driver, path):
    ''' `path` will usually be 
        https://www.browserstack.com/guide/xpath-in-selenium
        <a> = .//a[contains]
        <button> = .//button[contains(@onclick, 'Login()')]
    
    '''
    el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, path)))
    return el

def get_current_activities(driver):
    now = datetime.now()
    max_activities = 100
    activities = 0 
    data=[]
    table = wait_to_click(driver, ".//table")
    headers =   [
                header.text 
                for header
                in table.find_elements(By.XPATH, "//th")
                ]
    for row in table.find_elements(By.XPATH,".//tr[position()>1]"):
        cells = row.find_elements(By.XPATH, ".//td")
        row_data = {}
        for i, cell in enumerate(cells):
            row_data[headers[i]] = cell.text
            if cell.text == "View":
                button = row.find_element(By.XPATH, ".//button")
                row_data[headers[i]] = button.get_attribute("onclick")
        data.append(row_data)
        activities += 1
        if activities > max_activities:
            break
        if parse_date(row_data['Start Date']) < now:
            break
    return data


def dateandtitle(activities):
    existing_dates = [(parse_date(activity["Start Date"]).date(),activity['Title']) for activity in activities]
    return existing_dates

def checkifduplicate(row, activities):
    print('checking for duplicate')
    row_date = parse_date(row[0]).date()
    dates_and_titles = dateandtitle(activities)
    for date_title_tuple in dates_and_titles:
        if row_date == date_title_tuple[0] and row[2].strip() == date_title_tuple[1].strip():
            return True
    return False

def update_id(driver, id, value):
    el = driver.find_element(By.ID, id)
    el.clear()
    el.send_keys(value)
    return None

def create_activity(driver, row):
    date, end, title, outing_type, allday, startTime, endTime, location, remarks, description, registration, delete = row
    startDateTime = f"{date} {startTime}"
    endDateTime = f"{end} {endTime}"
    activity = wait_to_click(driver, ".//a[contains(@onclick, 'ActivityAddNew()')]")
    activity.click()

    #initial popup
    if not outing_type == "Meeting":
        activity_type = wait_to_click(driver, f"//*[text()='{outing_type}']")
        activity_type.click()
    activity = wait_to_click(driver, ".//input[contains(@id, 'StartDate')]")
    activity.clear()
    activity.send_keys(date)
    activity = wait_to_click(driver, ".//a[contains(@class, 'btn-danger')]")
    activity.click()
    time.sleep(5)
  
    if allday == "no":
        driver.find_element(By.ID, "AllDay").click()
        time.sleep(2)
        update_id(driver, "StartDateTime", startDateTime)
        update_id(driver, "EndDateTime", endDateTime)
    else:
        update_id(driver, "StartDate", date)
        update_id(driver, "EndDate", end)

    update_id(driver, "Title", title)
    update_id(driver, "Location", location)
    update_id(driver, "Remarks", remarks)
    update_id(driver, "Description", description)

    #implement registrations if desired
    
    if delete == "yes":
        time.sleep(5)
        activity = wait_to_click(driver, "//*[text()='Delete / Archive']")
        activity.click()
        time.sleep(0.5)
        driver.find_element(By.ID, "Delete").click()
        activity = wait_to_click(driver, ".//button[contains(@onclick, 'DeleteActivity()')]")
        activity.click()
    else:
        driver.find_element(By.ID, "save").click()
        time.sleep(1)
        activity = wait_to_click(driver, ".//button[contains(@onclick, 'closeactivity()')]")
        activity.click()
        time.sleep(10)
    return True

def fill_form2(data):
    #startup
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options)
    driver.get("https://tmweb.troopmaster.com/mysite/Troop680")
    
    #login 
    login = wait_to_click(driver, ".//a[contains(@onclick, 'Login()')]")
    login.click()
    driver.find_element(By.ID, "userid").send_keys(USER)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    login = wait_to_click(driver, ".//button[contains(@onclick, 'Login()')]")
    login.click()
    time.sleep(3)
    
    # Get to activity Page
    driver.get("https://tmweb.troopmaster.com/ActivityManagement/index")
    expand = wait_to_click(driver, "//a[text()='Show All Activities']")
    expand.click()
    time.sleep(9)
    activities = get_current_activities(driver)
    
    # Check if activity is already on the activity list, if it is, skip
    max_number_of_creations = 50
    created = 0
    for row in data:
        duplicate = checkifduplicate(row, activities)
        if duplicate:
            print(f"Duplicate activity {row[2]} on {row[0]}")
            print("Skipping....")
            continue
        create_activity(driver, row)
        print(f"Created activity {row[2]} on {row[0]}")
        driver.get("https://tmweb.troopmaster.com/ActivityManagement/index")
        time.sleep(3)
        created += 1
        if created >= max_number_of_creations:
            print('exceeded number of created items at a time')
            print('exiting')
            break


    # Clean UP
    time.sleep(3)
    driver.quit()


# Main function to read CSV and fill out forms
def main(csv_file):
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        data = [row for row in reader]
    return data

stub_data = [[
"05/03/2024",
"05/03/2024",
"Troop Meeting",
"Meeting",
"no",
"7:00 PM",
"8:30 PM",
"RBCC (17010 Pomerado Rd, San Diego, CA 92128)",
"Weekly troop meeting",
"We do NOT have Troop meetings when there is a Poway Unified School District No-school (e.g., holidays).",
"no",
"no",
],
[
"05/04/2024",
"05/04/2024",
"Troop Meeting",
"Meeting",
"no",
"7:00 PM",
"8:30 PM",
"RBCC (17010 Pomerado Rd, San Diego, CA 92128)",
"Weekly troop meeting",
"We do NOT have Troop meetings when there is a Poway Unified School District No-school (e.g., holidays).",
"no",
"no",
]
]
# Call main function with the CSV file path
if __name__ == "__main__":
    data = main("meetings.csv")  # Replace with the path to your CSV file
    #data = stub_data
    fill_form2(data)
