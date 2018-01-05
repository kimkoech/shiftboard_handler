# program that opens an address in chrome and automatically logs in
# designed for shiftboard

from selenium import webdriver
import time
from datetime import datetime, timedelta

# import wait modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# variables
estimated_total_running_time = 0
address = 'https://www.shiftboard.com/log-in/'  # shiftboard website address
email = 'bkkoech@college.harvard.edu'
password = 'nicholaskoech1'
shiftDict = {}

# open web browswer
driver = webdriver.Chrome('/Users/Billy/projects/shiftboard_handler/chromedriver')
driver.get(address)  # open the address


# alternative that waits for webdriver
# variables
MaxDelay = 10
element_present = EC.presence_of_element_located  # condition for one element
elements_present = EC.presence_of_all_elements_located  # condition for multiple elements


# function that waits for elements to be available
def patiently_find(_driver, condition, locator_by_type, el_locator):
    try:
        wait = WebDriverWait(_driver, MaxDelay)
        email_element = wait.until(condition((locator_by_type, el_locator)))
        return email_element
    except TimeoutException:
        print(TimeoutException + ": Finding " + el_locator + " by " + locator_by_type + " failed ")
    else:
        print("Something else went wrong when finding " + el_locator + " by " + locator_by_type)


email_id = 'et_pb_email_1'


# Insert username and password
email_field = patiently_find(driver, element_present, By.ID, email_id)
email_field.send_keys(email)  # insert email address text
password_field = driver.find_element_by_id('password_input')
password_field.send_keys(password)  # insert password text

# simulate a human; wait for a second or two


# submit and log in
login_button = driver.find_element_by_class_name('login-submit-btn')
driver.execute_script("window.scrollTo(0, 250);")
login_button.click()  # click log in
print("Logging in successful!")


time.sleep(1)

# go to two weeks ahead
next_week_button = driver.find_element_by_xpath('//*[@id="leftapp"]/div[1]/a[3]')
next_week_button.click()  # go to 1 week ahead

time.sleep(1)
# retrieve new address for next button to prevent stale element referral
next_week_button = driver.find_element_by_xpath('//*[@id="leftapp"]/div[1]/a[3]')
next_week_button.click()  # go to 2 weeks ahead

time.sleep(1)

######################## third week for testing #####################
# retrieve new address for next button to prevent stale element referral
next_week_button = driver.find_element_by_xpath('//*[@id="leftapp"]/div[1]/a[3]')
next_week_button.click()  # go to 3 weeks ahead

time.sleep(1)
###################################################################

# scrap website of two weeks ahead
# list of all shifts
#shift_times = driver.find_elements_by_class_name('shifthead')
#days_of_the_week = driver.find_elements_by_css_selector('.wkday.top.weekcol')
# dates_of_the_week = driver.find_elements_by_css_selector('.bold.clu.dayno')
#shifts_in_the_week = driver.find_elements_by_css_selector('.clu.popout.fine.row_unconfirmed')
#shift_locations = driver.find_elements_by_css_selector('.wkday.bold.popout.fine.sb-team-header')

# printing tests:
# print("Shift times:", shift_times)
# print("Days of the week:", days_of_the_week)
# print("Dates of the week:", dates_of_the_week)
# print("Shifts in the week:", shifts_in_the_week)
# print("Shift locations:", shift_locations)

# for element in shift_times:
# 	print(element.get_attribute('innerHTML'))
# for element in dates_of_the_week:
# 	print(element.get_attribute('innerHTML'))

# test variables
table_data = 'td'

# scrap table row element with all shifts
shift_table = driver.find_element_by_xpath('//*[@id="leftapp"]/table[2]/tbody/tr')
# shift_days = shift_table.find_elements_by_tag_name()  # each child is a day
shift_days = patiently_find(shift_table, elements_present, By.TAG_NAME, table_data)

time.sleep(1)  # delay


def get_inner_HTML(el):
    return el.get_attribute('innerHTML')


def utf8_encoder(unicoded_string):
    return unicoded_string.encode('utf-8')


def clean_data(string_data):
    temp = string_data.replace(" ", "")  # remove all spaces
    return temp


def hyphen_splitter(string_data):
    temp = string_data.replace("-", " ").split(" ")
    return temp


# get the date from the website
website_date = driver.find_element_by_xpath('//*[@id="leftapp"]/div[1]/a[2]')
innerWebsiteDate = get_inner_HTML(website_date)
innerWebsiteDate = innerWebsiteDate.replace(",", "")  # remove all commas
innerWebsiteDate = innerWebsiteDate.split(" ")  # split first from last date

# dict for months
monthDict = {	'Jan': 1,
              'Feb': 2,
              'Mar': 3,
              'Apr': 4,
              'May': 5,
              'Jun': 6,
              'Jul': 7,
              'Aug': 8,
              'Sep': 9,
              'Oct': 10,
              'Nov': 11,
              'Dec': 12	}

# store date values in variables
website_month = utf8_encoder(innerWebsiteDate[0])
website_month = monthDict[website_month]
website_day = utf8_encoder(innerWebsiteDate[1])
website_day = int(website_day)
website_year = utf8_encoder(innerWebsiteDate[2])
website_year = int(website_year)

# convert to datetime format:
website_datetime = datetime(website_year, website_month, website_day)

list_days_with_datetimes = []
# increment date and make tuple list of [(day, date)]
for i in range(0, 7):
    incremented_date = website_datetime + timedelta(days=i)
    day = incremented_date.strftime('%d')
    list_days_with_datetimes.append((day, incremented_date))


for day in shift_days:
    date_of_the_week = day.find_element_by_css_selector('.bold.clu.dayno')  # get date of day
    innerDate = date_of_the_week.get_attribute('innerHTML')
    innerDate = utf8_encoder(innerDate)  # encode into a string
    shift_times = day.find_elements_by_class_name('shifthead')  # get shifts of the day
    innerTimes = map(get_inner_HTML, shift_times)
    innerTimes = map(utf8_encoder, innerTimes)  # encode into a string
    innerTimes = map(clean_data, innerTimes)  # remove spaces
    innerTimes = map(hyphen_splitter, innerTimes)
    shift_locations = day.find_elements_by_css_selector('.wkday.bold.popout.fine.sb-team-header')  # location that corresponds to shift
    innerLocations = map(get_inner_HTML, shift_locations)
    innerLocations = map(utf8_encoder, innerLocations)
    shift_clickable_el = day.find_elements_by_css_selector('.clu.popout.fine.row_unconfirmed')
    shiftDict[innerDate] = zip(innerTimes, innerLocations, shift_clickable_el)


print(website_datetime)
print(list_days_with_datetimes)


# replace shiftDict keys with datetimes
for _day, _date in list_days_with_datetimes:
    shiftDict[_date] = shiftDict.pop(_day)

print(shiftDict)

# test values for grab shift
test_dateAndTime = datetime(2018, 01, 27, 20)

# function that grabs shifts, take datetime.datetime
# sample of dictValues
"""
[	(['9am', '11am'], 'Lab Assistance - Lamont', <element>), 
	(['11am', '12pm'], 'Lab Assistance - Lamont', <element>), 
	(['12pm', '1pm'], 'Lab Assistance - Lamont', <element>)		]
"""


def grab_shift(date_and_time):
    bare_y, bare_m, bare_d = date_and_time.strftime("%Y/%m/%d").split("/")
    plain_date = datetime(int(bare_y), int(bare_m), int(bare_d))
    formated_hour = date_and_time.strftime("%I%p").lower().lstrip("0")
    # check if shift is available
    if plain_date in shiftDict:
        dictValues = shiftDict[plain_date]  # find shifts in plain_date
        for shiftDateRange, shiftLocation, clickElement in dictValues:
            # Name shiftDataRange elements for readability
            shiftStartTime = shiftDateRange[0]
            shiftEndTime = shiftDateRange[1]  # currently not in use
            # find shift by compring times
            if shiftStartTime == formated_hour:
                # click to grab shift
                clickElement.click()
                time.sleep(1)  # wait for page to load
                # find "take this shift button"
                TakeThisShift = driver.find_element_by_xpath('//*[@id="rightapp"]/div[5]/div[3]/form/button')
                TakeThisShift.click()  # click to take shift
                # time.sleep(1) #wait for page to load
                #ConfirmShift = driver.find_element_by_xpath('//*[@id="assignment"]/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button[1]')
                # ConfirmShift.click() #click to confirm shift
                print('Shift grabbing completed at: ', datetime.now().strftime("%I:%M %p"))
            else:
                print(shiftStartTime, ": Time mismatch or shift unavailable, skipping...")
    else:
        print("Date mismatch")


grab_shift(test_dateAndTime)


time.sleep(5)  # Let the user actually see something!
driver.quit()  # close browser after done
print("Simulation successful")
