################################################################################
"""
Program that opens chrome web browser and automatically logs in.
Specifically designed for shiftboard, but some code can be furhter abstaracted
and used on other websites
"""

# import modules
from selenium import webdriver
from datetime import datetime, timedelta
import time
# wait modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# program global variables
chromedriver = '/Users/Billy/projects/shiftboard_handler/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')        # hide chrome window --headless
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(chromedriver, chrome_options=options)
shiftDict = {}
DebugMode = False
monthDict = {'Jan': 1,
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
             'Dec': 12	}  # dict for months
FindTimeout = 10  # variable for max time taken to find element in seconds
# conditions used when invoking patiently_find(). These variables are functions
element_present = EC.presence_of_element_located  # condition for one element
elements_present = EC.presence_of_all_elements_located  # condition for multiple elements


# shiftboard HTML related variables
emailFieldId = 'et_pb_email_1'
passwordFielId = 'password_input'
loginButtonClass = 'login-submit-btn'
nxtWeekBtnXpath = '//*[@id="leftapp"]/div[1]/a[3]'
tableRowXpath = '//*[@id="leftapp"]/table[2]/tbody/tr'
shiftColumnsTag = 'td'
dateCSSselector = '.bold.clu.dayno'
shiftTimesClass = 'shifthead'
LocationsCSSselector = '.wkday.bold.popout.fine.sb-team-header'
grabCSSselector = '.clu.popout.fine.row_unconfirmed'
dateRangeXpath = '//*[@id="leftapp"]/div[1]/a[2]'
TakeThisShiftXpath = '//*[@id="rightapp"]/div[5]/div[3]/form/button'
ConfirmShiftXpath = '//*[@id="assignment"]/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button[1]'


# user variables(can be used to invoke functions from outside this module)

# function that uses WebDriverWait to wait for all elements to load
# driver can be an element with children
# conditions are provided above in variables
def patiently_find(_driver, condition, locator_by_type, el_locator):
    try:
        wait = WebDriverWait(_driver, FindTimeout)
        foundElement = wait.until(condition((locator_by_type, el_locator)))
        return foundElement
    except TimeoutException:
        print(TimeoutException + ": Finding " + el_locator + " by " + locator_by_type + " failed")
    else:
        print("Something else went wrong when finding " + el_locator + " by " + locator_by_type)


# function that waits for stale elements to reload
def wait_for_stale_elements(_driver, stale_elements):
    # wait until previous element is stale
    WebDriverWait(_driver, FindTimeout).until(EC.staleness_of(stale_elements))


# function that opens url on browser
def launch_browser(url):
    driver.get(url)
    print("Browser launched...")


# function that logs user in
def login(email_address, user_password):
    email_field = patiently_find(driver, element_present, By.ID, emailFieldId)
    email_field.send_keys(email_address)		# insert email address text
    password_field = patiently_find(driver, element_present, By.ID, passwordFielId)
    password_field.send_keys(user_password)  	# insert password text
    login_button = patiently_find(driver, element_present, By.CLASS_NAME, loginButtonClass)
    driver.execute_script("window.scrollTo(0, 250);")
    login_button.click() 						# click log in
    # print succes message when log in is successful
    WebDriverWait(driver, login_button)
    print("Logging in successful!")


# function to simulate human delays
def delay(time_in_seconds):
    time.sleep(time_in_seconds)


# function to go to the next week as many as "repeat" times
# this function call wait_for_stale_elements when exiting thus ensuring that
# a page is reloaded when exiting
def goto_next_week(repeat):
    for _ in range(repeat):
        next_week_button = patiently_find(driver, element_present, By.XPATH, nxtWeekBtnXpath)
        next_week_button.click()
        # wait for page to reload
        wait_for_stale_elements(driver, next_week_button)


# gets the inner HTML of an element
# helper function of shiftboard_parser
def get_inner_HTML(el):
    return el.get_attribute('innerHTML')


# function that removes unicode characters
# helper function for shiftboard_parser
def utf8_encoder(unicoded_string):
    return unicoded_string.encode('utf-8')


# function that remove spaces
# helper function for shiftboard_parser
def clean_data(string_data):
    temp = string_data.replace(" ", "")  # remove all spaces
    return temp


# function to split date range at the hyphen
def hyphen_splitter(string_data):
    temp = string_data.replace("-", " ").split(" ")
    return temp


# function to grab date from page (takes dateRangeXpath in dict_date_converter)
# helper function for dict_date_converter
def first_day_date_retreiver(date_xpath):
    website_date = patiently_find(driver, element_present, By.XPATH, date_xpath)
    innerWebsiteDate = get_inner_HTML(website_date)
    # remove all commas
    innerWebsiteDate = innerWebsiteDate.replace(",", "")
    # split date parts into a list
    innerWebsiteDate = innerWebsiteDate.split(" ")
    # extract month and convert to int
    website_month = utf8_encoder(innerWebsiteDate[0])
    website_month = monthDict[website_month]
    # extract day and convert to int
    website_day = utf8_encoder(innerWebsiteDate[1])
    website_day = int(website_day)
    # extract year and convert to int
    website_year = utf8_encoder(innerWebsiteDate[2])
    website_year = int(website_year)
    # convert to datetime format
    website_datetime = datetime(website_year, website_month, website_day)
    return website_datetime


# function that reformats the date using datetime (takes shiftDict in shiftboard_parser)
# helper function for shiftboard_parser
def dict_date_converter(mydict):
    list_days_with_datetimes = []  # variable to hold list of (day,datetime)
    # increment date and make tuple list of [(day, date)]
    for i in range(0, 7):
        incremented_date = first_day_date_retreiver(dateRangeXpath) + timedelta(days=i)
        incremented_day = incremented_date.strftime('%d')
        list_days_with_datetimes.append((incremented_day, incremented_date))
    # replace days in mydict ie. shiftDict with datetimes
    for _day, _date in list_days_with_datetimes:
        mydict[_date] = mydict.pop(_day)  # pop day and replace with date
    return mydict


# function to parse data in shiftboard.
# Returns a dict eg {datetime: (innertimes, innerLocations, shift_clickable_el)}
# dict shows available shift hours
# takes tableRowXpath in grab_shift
def shiftboard_parser(table_row_xpath):
    shift_table = patiently_find(driver, element_present, By.XPATH, table_row_xpath)
    shift_days = patiently_find(shift_table, elements_present, By.TAG_NAME, shiftColumnsTag)
    # delay(1)									# short delay, currently removed
    # make a dict from the table data.
    for day in shift_days:
        # get element of date of day
        date_of_the_week = patiently_find(day, element_present, By.CSS_SELECTOR, dateCSSselector)
        innerDate = get_inner_HTML(date_of_the_week)
        innerDate = utf8_encoder(innerDate)					# remove unicode chars
        # get element of the times of shifts of the day, and get innerHTLM
        shift_times = patiently_find(day, elements_present, By.CLASS_NAME, shiftTimesClass)
        innerTimes = map(get_inner_HTML, shift_times)
        innerTimes = map(utf8_encoder, innerTimes)				# encode into a string
        innerTimes = map(clean_data, innerTimes)				# remove spaces
        innerTimes = map(hyphen_splitter, innerTimes)			# split time ranges
        # get elements of the locations of the shifts, and get innerHTLM
        shift_locations = patiently_find(day, elements_present, By.CSS_SELECTOR, LocationsCSSselector)
        innerLocations = map(get_inner_HTML, shift_locations)
        innerLocations = map(utf8_encoder, innerLocations)		# encode into a string
        # get elements to be clicked when grabbing shifts
        shift_clickable_el = patiently_find(day, elements_present, By.CSS_SELECTOR, grabCSSselector)
        # create dict
        shiftDict[innerDate] = zip(innerTimes, innerLocations, shift_clickable_el)
    # convert date in dict to datetime.datetime type
    converted_shiftDict = dict_date_converter(shiftDict)
    # troubleshooting
    if DebugMode:
        print(converted_shiftDict)
    # return parsed data
    return converted_shiftDict


#########################################################
"""
# function that grabs shifts, takes datetime.datetime
# sample of dictValues

[	(['9am', '11am'], 'Lab Assistance - Lamont', <element>),
	(['11am', '12pm'], 'Lab Assistance - Lamont', <element>),
	(['12pm', '1pm'], 'Lab Assistance - Lamont', <element>)		]

# sample date_and_time input made from invoking datetime()
test_dateAndTime = datetime(2018,01,27,20)
"""
#########################################################


def grab_shift(date_and_time):
        # find shifts in shiftboard
    available_shifts = shiftboard_parser(tableRowXpath)
    # extract just the date from input
    bare_y, bare_m, bare_d = date_and_time.strftime("%Y/%m/%d").split("/")
    plain_date = datetime(int(bare_y), int(bare_m), int(bare_d))
    # extract  just the hour from input and format it
    formated_hour = date_and_time.strftime("%I%p").lower().lstrip("0")
    # find shift
    if plain_date in available_shifts:
        # get shifts and shifts' info on plain_date
        dictValues = available_shifts[plain_date]
        for shiftDateRange, shiftLocation, clickElement in dictValues:
            # Name shiftDataRange elements for readability
            shiftStartTime = shiftDateRange[0]
            # shiftEndTime = shiftDateRange[1] 	# currently not in use
            # find shift by comparing date_and_time to shift hours
            if shiftStartTime == formated_hour:
                # indicate that shift has been found
                print(shiftStartTime + ": match found, deploying confirm button...")
                clickElement.click() 	# click to grab shift
                # find "take this shift button"
                TakeThisShift = patiently_find(driver, element_present, By.XPATH, TakeThisShiftXpath)
                TakeThisShift.click() 	# click to take shift
                # find "confirm shift" button
                ConfirmShift = patiently_find(driver, element_present, By.XPATH, ConfirmShiftXpath)
                # Return confirm shift button
                print('Confirm button deployed at: ' + datetime.now().strftime("%I:%M:%S %p"))
                return ConfirmShift

            else:
                print(shiftStartTime + ": Time mismatch or shift unavailable, skipping...")
    else:
        print("Date mismatch")


# function to click confirm shift
def confirm_shift(confirm_button):
    confirm_button.click()  # click to confirm shift
    # print confirmation message when ConfirmShift page is stale
    wait_for_stale_elements(driver, confirm_button)
    print('Shift confirmed at: ' + datetime.now().strftime("%I:%M:%S %p"))


# function to close browser
def exit_sequence():
    driver.quit()  # close browser after done
