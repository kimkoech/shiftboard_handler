# program that opens an address in chrome and automatically logs in
# designed for shiftboard

from selenium import webdriver
import time
from datetime import datetime, timedelta
from lxml import etree, html

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
debugMode = True

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
# shift_times = driver.find_elements_by_class_name('shifthead')
# days_of_the_week = driver.find_elements_by_css_selector('.wkday.top.weekcol')
# dates_of_the_week = driver.find_elements_by_css_selector('.bold.clu.dayno')
# shifts_in_the_week = driver.find_elements_by_css_selector('.clu.popout.fine.row_unconfirmed')
# shift_locations = driver.find_elements_by_css_selector('.wkday.bold.popout.fine.sb-team-header')

# printing tests:
# print("Shift times:", shift_times)
# print("Days of the week:", days_of_the_week)
# print("Dates of the week:", dates_of_the_week)
# print("Shifts in the week:", shifts_in_the_week)
# print("Shift locations:", shift_locations)

# for element in shift_times:
#   print(element.get_attribute('innerHTML'))
# for element in dates_of_the_week:
#   print(element.get_attribute('innerHTML'))

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
             'Dec': 12}

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
    list_days_with_datetimes.append((day.lstrip("0"), incremented_date))


for day in shift_days:
    date_of_the_week = day.find_element_by_css_selector('.bold.clu.dayno')  # get date of day
    innerDate = date_of_the_week.get_attribute('innerHTML')
    innerDate = utf8_encoder(innerDate)  # encode into a string
    shift_times = day.find_elements_by_class_name('shifthead')  # get shifts of the day
    innerTimes = map(get_inner_HTML, shift_times)
    innerTimes = map(utf8_encoder, innerTimes)  # encode into a string
    innerTimes = map(clean_data, innerTimes)  # remove spaces
    innerTimes = map(hyphen_splitter, innerTimes)
    print("innerTimes: \n")
    print(innerTimes)
    shift_locations = day.find_elements_by_css_selector('.wkday.bold.popout.fine.sb-team-header')  # location that corresponds to shift
    innerLocations = map(get_inner_HTML, shift_locations)
    innerLocations = map(utf8_encoder, innerLocations)
    print("innerLocations \n")
    print(innerLocations)
    shift_clickable_el = day.find_elements_by_css_selector('.clu.popout.fine')  # .row_unconfirmed')
    shiftDict[innerDate] = zip(innerTimes, innerLocations, shift_clickable_el)


print("website datetime: \n")
print(website_datetime)

print("days with datetimes : \n")
print(list_days_with_datetimes)


# replace shiftDict keys with datetimes
for _day, _date in list_days_with_datetimes:
    shiftDict[_date] = shiftDict.pop(_day)


# test values for grab shift
test_dateAndTime = datetime(2018, 01, 27, 20)

# function that grabs shifts, take datetime.datetime
# sample of dictValues
"""
[   (['9am', '11am'], 'Lab Assistance - Lamont', <element>),
    (['11am', '12pm'], 'Lab Assistance - Lamont', <element>),
    (['12pm', '1pm'], 'Lab Assistance - Lamont', <element>)     ]
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
                # ConfirmShift = driver.find_element_by_xpath('//*[@id="assignment"]/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button[1]')
                # ConfirmShift.click() #click to confirm shift
                print('Shift grabbing completed at: ', datetime.now().strftime("%I:%M %p"))
            else:
                print(shiftStartTime, ": Time mismatch or shift unavailable, skipping...")
    else:
        print("Date mismatch")


# sketch for converting webelement to xml elements and finding xpath:
"""


test_Webelement = driver.find_element_by_xpath('//*[@id="leftapp"]/table[2]/tbody/tr/td[1]')
html_string = test_Webelement.get_attribute('innerHTML')
root = html.fromstring(html_string)
tree = etree.ElementTree(root)
all_headers = root.xpath("//div[@class='wkday bold popout fine sb-team-header']")
# lamont_header = driver.find_element_by_xpath('//*[@id="leftapp"]/table[2]/tbody/tr/td[6]/div[10]')
# e2 = html.fromstring(lamont_header.get_attribute('innerHTML'))

print ("printing all header elements in list: \n")
print(all_headers)

print ("printing all xpaths of all headers: \n")
for elemnt in all_headers:
    print(tree.getpath(elemnt))
    print("\n")

# print tree.getpath(e2)
# print ("printing lamont path: \n")
# print tree.getpath(e2)


print("this is the root: \n")
print(root.iter())
print("\n")
print("this is the tree:")
print(tree)

"""


# function to make searchable tree from element
# used when retrieving xpath
def make_tree(lxml_element):
    _tree = etree.ElementTree(lxml_element)
    return _tree


# function to get shift table lxml element and make element list of shift days
# returns lmxl element list
"""
Abandoned because it failed to work as expected
"""


def get_lxml_shift_days(table_webelement):
        # get innner html of table row
    _html_string = table_webelement.get_attribute('innerHTML')
    # convert to lxml element
    table_lxml_el = html.fromstring(_html_string)
    if debugMode:
        print("This is what the table element looks like: (from inside get_lxml_shift_days) : \n")
        print(table_lxml_el)
    else:
        pass  # ignore
    # get days by class top cal-week-add return list of days ie list of elements
    lxml_els_days = table_lxml_el.xpath("//td[@class='top cal-week-add']")
    return lxml_els_days

# funtion that converts WebElement to lxml element
# return lxml element


def webelement_to_lxml_element(webelement_el):
        # get inner html string
    _html_string = webelement_el.get_attribute('innerHTML')
    # convert to lxml element
    return html.fromstring(_html_string)


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
    print("This is the list of day 0, expect 4: \n")
    print(el_location_list)
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


'''Not yet added to browser_handler module'''
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


# troubleshooting tests
if debugMode:
    # test if we get list of days
    """
    Abondoned
    """
    # test_table = driver.find_element_by_xpath('//*[@id="leftapp"]/table[2]/tbody/tr')
    # test_days = get_lxml_shift_days(test_table)
    # print("list of elements by get_lxml_shift_days, expect 7 : \n")
    # print(test_days)

    # test if we get xpath of locations from day, tested with first day of week
    # also tests webelement_to_lxml_element function
    first_day = driver.find_element_by_xpath('//*[@id="leftapp"]/table[2]/tbody/tr/td[1]')
    first_day = webelement_to_lxml_element(first_day)
    # first_day = first_day.get_attribute('innerHTML')
    # first_day = html.fromstring(first_day)
    first_day_xpaths = get_xpaths_of_locations(first_day)
    print("list of xpaths from first day of week by get_xpaths_of_locations : \n")
    print(first_day_xpaths)

    # test if extraction of last number works
    extracted_ints = map(extract_number_from_xpath, first_day_xpaths)
    print("list of extracted numbers from xpaths of first day of week by extract_number_from_xpath : \n")
    print(extracted_ints)

    # test if index function works
    indices_found = find_sharing_shifts(extracted_ints)
    print("this is the list of time indices that should be duplicated : \n")
    print(indices_found)


else:
    pass  # do nothing


print("shiftdict: \n")
print("\n")
print(shiftDict)

# grab_shift(test_dateAndTime)

# tests for browser handler
# test_available_shifts = test_BH.shiftboard_parser(test_BH.tableRowXpath)

# print("Test for shiftboard parser: \n")
# print(test_available_shifts)


time.sleep(5)  # Let the user actually see something!
driver.quit()  # close browser after done
print("Simulation successful")
