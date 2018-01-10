################################################################################
"""
Program that opens chrome web browser and automatically logs in.
Specifically designed for shiftboard, but some code can be furhter abstaracted
and used on other websites

created by Billy Koech
Date Jan 4th 2018
mru
Jan 6th 2018 - added mru
Jan 6th 2018 - imported (from lxml import etree, html)
Jan 6th 2018 added the following functions:
                    webelement_to_lxml_element
                    make_tree
                    get_xpath_from_lxml
                    get_xpaths_of_locations
                    extract_number_from_xpath
Jan 7th 2018 - added the following functions:
                    find_sharing_shifts
                    create_time_duplicate
                    changed grabCSSselector = '.clu.popout.fine.row_unconfirmed'
                    to grabCSSselector = '.clu.popout.fine'
Jan 8th 2018 -  imported today_raw_date from scheduler
                created and tested extract_day_shift_time


"""

# import modules
from selenium import webdriver  # enables interface with chrome browser
from datetime import datetime, timedelta  # used with everything time related
import time
from lxml import etree, html  # used to get xpath
from scheduler import today_raw_date, date_to_tuple  # function for extracting raw date
# wait modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# program global variables
chromedriver = '/Users/Billy/projects/shiftboard_handler/chromedriver'
######## comment these out to disable headless mode#########
# options = webdriver.ChromeOptions()
# options.add_argument('headless')        # hide chrome window --headless
# options.add_argument('window-size=1200x600')
#############################################################
driver = webdriver.Chrome(chromedriver)  # , chrome_options=options)
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
             'Dec': 12}  # dict for months
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
grabCSSselector = '.clu.popout.fine'
dateRangeXpath = '//*[@id="leftapp"]/div[1]/a[2]'
TakeThisShiftXpath = '//*[@id="rightapp"]/div[5]/div[3]/form/button'
ConfirmShiftXpath = '//*[@id="assignment"]/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button[1]'
clickTextTagName = 'span'

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
        print(TimeoutException, ": Finding " + el_locator + " by " + locator_by_type + " failed")
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
    email_field.send_keys(email_address)        # insert email address text
    password_field = patiently_find(driver, element_present, By.ID, passwordFielId)
    password_field.send_keys(user_password)     # insert password text
    login_button = patiently_find(driver, element_present, By.CLASS_NAME, loginButtonClass)
    driver.execute_script("window.scrollTo(0, 250);")
    login_button.click()                        # click log in
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


# funtion that converts WebElement to lxml element
# return lxml element
def webelement_to_lxml_element(webelement_el):
    # get inner html string
    _html_string = webelement_el.get_attribute('innerHTML')
    # convert to lxml element
    return html.fromstring(_html_string)


# function to make searchable tree from element
# used when retrieving xpath
def make_tree(lxml_element):
    _tree = etree.ElementTree(lxml_element)
    return _tree


# function to extract xpath from element
# takes parent tree and the element to be extracted
def get_xpath_from_lxml(lxml_tree, lxml_element):
    return lxml_tree.getpath(lxml_element)


# function to get xpath of the locations in the day
# take day lxml element, returns list of xpaths
# helper functions: make_tree(), get_xpath_from_lxml()
def get_xpaths_of_locations(day_element):
    # make locations- list of lxml elements
    el_location_list = day_element.xpath("//div[@class='wkday bold popout fine sb-team-header']")
    # troubleshooting
    if DebugMode:
        print("This is the list of elements of the day by get_xpaths_of_locations: \n")
        print(el_location_list)
    else:
        pass  # ignore
    # turn day_element into a tree, used below when searching for element
    day_tree = make_tree(day_element)
    # get the xpath of elements in list
    _list_output = []  # empty list to populate with data below
    for el in el_location_list:
        _list_output.append(get_xpath_from_lxml(day_tree, el))
    # return list of xpaths of locations
    return _list_output


# function to extract last number from xpath
# returns number
def extract_number_from_xpath(loc_xpath):
    # get last two characters
    last_two = loc_xpath[-2:]
    # strip last character and return number
    return int(last_two[0:1])


# function to find indeces of shifts that share time using xpath
# returns index of shift time in a list
def find_sharing_shifts(num_list):
    timeindices = []
    i = 0
    for x, y in zip(num_list, num_list[1:]):
        plus_one_mode_of_x = (x + 1) % 10
        if plus_one_mode_of_x == y:
            timeindices.append(i)
        else:
            i += 1
    return timeindices


# function that adds time duplicates to innerTime list
def create_time_duplicates(time_list, indices_list):
    new_list = time_list
    store_times = []
    for index in indices_list:
        # find time and store
        store_times.append(new_list[index])
    # because indices will change, find new indices and duplicate
    for _time in store_times:
        new_index = new_list.index(_time)
        # insert duplicate at index
        new_list.insert(new_index, _time)
    # return final list
    return new_list


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
        list_days_with_datetimes.append((incremented_day.lstrip("0"), incremented_date))
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
    # delay(1)                                  # short delay, currently removed
    # make a dict from the table data.
    for day in shift_days:
        # get element of date of day
        date_of_the_week = patiently_find(day, element_present, By.CSS_SELECTOR, dateCSSselector)
        innerDate = get_inner_HTML(date_of_the_week)
        innerDate = utf8_encoder(innerDate)                 # remove unicode chars
        # get element of the times of shifts of the day, and get innerHTLM
        # retrieving from day thus no need for patiently_find
        shift_times = day.find_elements_by_class_name(shiftTimesClass)
        innerTimes = map(get_inner_HTML, shift_times)
        innerTimes = map(utf8_encoder, innerTimes)              # encode into a string
        innerTimes = map(clean_data, innerTimes)                # remove spaces
        innerTimes = map(hyphen_splitter, innerTimes)           # split time ranges
        # get elements of the locations of the shifts, and get innerHTLM, innerLocations is a list
        shift_locations = day.find_elements_by_css_selector(LocationsCSSselector)
        # retrieving from day thus no need for patiently_find
        innerLocations = map(get_inner_HTML, shift_locations)
        innerLocations = map(utf8_encoder, innerLocations)      # encode into a string
        # get elements to be clicked when grabbing shifts, shift_clickable_el is a list
        # retrieving from day thus no need for patiently_find
        shift_clickable_el = day.find_elements_by_css_selector(grabCSSselector)
        # check if length for the three
        if len(innerTimes) == len(innerLocations) == len(shift_clickable_el):
            # create dict
            shiftDict[innerDate] = zip(innerTimes, innerLocations, shift_clickable_el)
        # if not the same then create time duplicates where necessary
        else:
            # convert day's webelement to lxml element
            lxml_day = webelement_to_lxml_element(day)
            # extract xpath of the locations in the day
            list_day_xpaths = get_xpaths_of_locations(lxml_day)
            # extract integers from list of xpaths
            list_ints_of_xpaths = map(extract_number_from_xpath, list_day_xpaths)
            # get indeces of sharing shifts
            indices_found = find_sharing_shifts(list_ints_of_xpaths)
            # finding missing times and create duplicates, then store back in innerTimes
            innerTimes = create_time_duplicates(innerTimes, indices_found)
            # zip final result
            shiftDict[innerDate] = zip(innerTimes, innerLocations, shift_clickable_el)
    # convert date in dict to datetime.datetime type
    converted_shiftDict = dict_date_converter(shiftDict)
    # troubleshooting
    if DebugMode:
        print(converted_shiftDict)
    # return parsed data
    return converted_shiftDict


"""
# Sample shiftdict
{<datetime>:    [   (['9am', '11am'], 'Lab Assistance - Lamont', <element>),
                    (['11am', '12pm'], 'Lab Assistance - Lamont', <element>),
                    (['12pm', '1pm'], 'Lab Assistance - Lamont', <element>)
                ]
}
#
"""


# function to filter out taken shifts from shiftdict
# returns shift dict
def remove_taken_shifts(parsed_table_dict):
    # variable for output
    _output_dict = {}
    # iterate over every key <datetime>
    for key in parsed_table_dict.keys():
        _list_shifts = parsed_table_dict[key]
        # variable to hold each shift
        _output_list = []
        # get clickable element as _element
        for _shiftDateRange, _shiftLocation, _element in _list_shifts:
            # get text inside <element>, no need for patiently find
            inner_Text_element = _element.find_element_by_tag_name(clickTextTagName)
            inner_Text = get_inner_HTML(inner_Text_element)  # get inner html
            inner_Text = utf8_encoder(inner_Text)  # encode to remove extra characters
            # find and take just the available shifts
            if inner_Text == 'Available':
                # store back in list
                available_tuple = (_shiftDateRange, _shiftLocation, _element)
                _output_list.append(available_tuple)
            else:
                # indicate that the shift has already been taken
                print("Filtering: " + key.strftime("%b %d %Y") + " " + _shiftDateRange[0] + "-" + _shiftDateRange[1] + " taken by " + inner_Text)
        # update output dict
        _output_dict[key] = _output_list
    # return final dict
    return _output_dict


# function to extract day's shifts times as a dict with values in the form of list of tuples
# delta is an int in weeks
# return one day's shifts with the day's date as the key
def extract_day_shift_time(parsed_table_dict, delta):
    # create variable to hold output
    output_list = []
    output_dict = {}
    # extract just the date from input and increment by delta weeks
    raw_date = today_raw_date()
    raw_date_weeks_from_now = raw_date + timedelta(weeks=delta)
    # ensure that the is in dict
    if raw_date_weeks_from_now in parsed_table_dict:
        # get shift info as a list  of tuples
        extracted_shifts = parsed_table_dict[raw_date_weeks_from_now]
        # iterate over list and get just the time
        for _shiftDateRange, _shiftLocation, _clickElement in extracted_shifts:
            # get start time and end times and make a tuple
            _shiftStartTime = _shiftDateRange[0]
            _shiftEndTime = _shiftDateRange[1]
            tuple_start_end = (_shiftStartTime, _shiftEndTime)
            # append tuple to output list
            output_list.append(tuple_start_end)
        # update output dict and return final dict
        output_dict[raw_date_weeks_from_now] = output_list
        return output_dict
    else:  # if shift in not in list thne list is empty
        print("Error, date is not in list of extracted time see extract_day_shift_time")


# function that converts shiftboard time format to datetime
# returns a list of tuples of datetimes
# assumes that input dict has just one shift
def shift_time_to_datetime_parser(_dict_of_shifts):
    # variable to hold output
    output_list = []
    # iterate over dict
    for key in _dict_of_shifts.keys():
        # get the tuple of the date in key
        _y, _m, _d = date_to_tuple(key)
        # iterate over list of shifts and convert
        for _startTime, _endTime in _dict_of_shifts[key]:
            # extract time _startTime and _endTime remove am and pm
            # make string of time
            start_string_of_time = str(_y) + "/" + str(_m) + "/" + str(_d) + " " + _startTime
            end_string_of_time = str(_y) + "/" + str(_m) + "/" + str(_d) + " " + _endTime
            # parse into datetime and create tuple
            final_startTime = datetime.strptime(start_string_of_time, "%Y/%m/%d %I%p")
            final_endTime = datetime.strptime(end_string_of_time, "%Y/%m/%d %I%p")
            time_tuple = (final_startTime, final_endTime)
            # append to output list
            output_list.append(time_tuple)
        # return final list of tuples
        return (key, output_list)


#########################################################
"""
# function that grabs shifts, takes datetime.datetime
# sample of dictValues

[   (['9am', '11am'], 'Lab Assistance - Lamont', <element>),
    (['11am', '12pm'], 'Lab Assistance - Lamont', <element>),
    (['12pm', '1pm'], 'Lab Assistance - Lamont', <element>)     ]

# sample date_and_time input made from invoking datetime()
test_dateAndTime = datetime(2018,01,27,20)
"""
# this function takes just the startime of the shift
#########################################################


def grab_shift(date_and_time_tuple, parsed_table, location_of_shift='Lab Assistance - Lamont'):
        # find shifts in shiftboard
    available_shifts = parsed_table  # shiftboard_parser(tableRowXpath)
    # variable for input_starTime and input_endTime
    inputStartTime = date_and_time_tuple[0]
    inputEndTime = date_and_time_tuple[1]
    # extract just the date from input
    bare_y, bare_m, bare_d = date_to_tuple(inputStartTime)
    plain_date = datetime(bare_y, bare_m, bare_d)
    # extract  just the hour from inputStartTime and inputEndTime and format it
    inputStartHour = inputStartTime.strftime("%I%p").lower().lstrip("0")
    inputEndHour = inputEndTime.strftime("%I%p").lower().lstrip("0")
    # find shift
    if plain_date in available_shifts:
        # get shifts and shifts' info on plain_date
        dictValues = available_shifts[plain_date]
        # Handle empty dictValues
        if dictValues == []:
            print("No shifts to grab today, or all shifts have already been taken")
            return None
        else:
            pass
        for shiftDateRange, shiftLocation, clickElement in dictValues:
            # Name shiftDataRange elements for readability
            shiftStartTime = shiftDateRange[0]
            shiftEndTime = shiftDateRange[1]
            # find shift by comparing shiftStartTime and shiftEndTime to shift hours
            if (shiftStartTime == inputStartHour) and (shiftEndTime == inputEndHour) and (shiftLocation == location_of_shift):
                # indicate that shift has been found
                print(shiftStartTime + "-" + shiftEndTime + " : " + shiftLocation + " : MATCH FOUND, deploying confirm button...")
                clickElement.click()    # click to grab shift
                # find "take this shift button"
                TakeThisShift = patiently_find(driver, element_present, By.XPATH, TakeThisShiftXpath)
                TakeThisShift.click()   # click to take shift
                # find "confirm shift" button
                ConfirmShift = patiently_find(driver, element_present, By.XPATH, ConfirmShiftXpath)
                # Return confirm shift button
                print('Confirm button deployed at: ' + datetime.now().strftime("%I:%M:%S %p"))
                return ConfirmShift

            elif (shiftStartTime != inputStartHour) and (shiftEndTime != inputEndHour) and (shiftLocation != location_of_shift):
                print(shiftStartTime + "-" + shiftEndTime + " : " + shiftLocation + ": Time and Location mismatch, skipping...")
            elif shiftLocation != location_of_shift:
                print(shiftStartTime + "-" + shiftEndTime + " : " + shiftLocation + ": Location mismatch. Input loaction is unpreferred.")
            elif (shiftStartTime != inputStartHour) and (shiftEndTime != inputEndHour):
                print(shiftStartTime + "-" + shiftEndTime + " : " + shiftLocation + ": Time mismatch. skipping...")
            else:
                print("Error in grab_shift function of browser_handler: None of the conditions match")
    elif plain_date not in available_shifts:
        print("Date mismatch")
        return None  # return None for error handling
    else:
        print("Something went wrong with grab_shift")
        return None  # return non if all do not match


# function to click confirm shift
def confirm_shift(confirm_button):
    if confirm_button is None:
        print("shift NOT confirmed, timestamp: " + datetime.now().strftime("%I:%M:%S %p"))
    else:
        confirm_button.click()  # click to confirm shift
        # print confirmation message when ConfirmShift page is stale
        wait_for_stale_elements(driver, confirm_button)
        print('Shift confirmed at: ' + datetime.now().strftime("%I:%M:%S %p"))


# function to close browser
def exit_sequence():
    print("Exit sequence initiated. Closing browser and exiting program.")
    driver.quit()  # close browser after done


# Main entry point for the script.
def main():
    # troubleshooting
    if DebugMode:
        # test for extract_day_shift_time
        sample = {
            datetime(2018, 1, 29, 0, 0):
            [
                (['9am', '11am'], 'Lab Assistance - Lamont', '<>'),
                (['11am', '12pm'], 'Lab Assistance - Lamont', '<>')
            ]
        }
        ouput_of_extract_day_shift_time = extract_day_shift_time(sample, 3)
        print("This is ouput_of_extract_day_shift_time: \n")
        print(ouput_of_extract_day_shift_time)
        # test for shift_time_to_datetime_parser
        sample = {datetime(2018, 1, 29, 0, 0): [('9am', '11am'), ('11am', '12pm')]}
        ouput_of_shift_time_to_datetime_parser = shift_time_to_datetime_parser(ouput_of_extract_day_shift_time)
        print("This is ouput_of_shift_time_to_datetime_parser: \n")
        print(ouput_of_shift_time_to_datetime_parser)
    else:
        pass  # do nothing

    # close browser
    exit_sequence()


if __name__ == '__main__':
    main()
