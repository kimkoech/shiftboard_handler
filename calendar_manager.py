###############################################################################
"""
Program that uses google calendar API to retrieve one's free time

Code skelelon by:   by Billy Koech
Date:       Jan 4th 2018

mru(most recent update):
Jan 5 2018 - Added program description
Jan 7 2018 - Created and tested :   get_calendar_data
                                    utf8_encoder
                                    get_timeslot_dict
                                    filter_out_busy_timeslots
                                    list_concat_consecutive_timeslots
                                    convert_timeslots_to_periods
                                    gtime_to_datetime_converter
                                    map_over_list_of_tuples
                                    dict_times_to_datetimes
                                    check_if_free_comparator
                                    retrieve_schedule_of_the_day
Jan 7 2018 -    changed all & to and
                moved requestDate to debugging section




"""
###############################################################################
# import modules
from datetime import datetime  # , timedelta  # import datetime module
import requests  # moudle for making GET requests
from scheduler import date_to_tuple  # function for extracting date in tuple form
import file_manager as FM

# program variables
busyFreeAPI_url = 'https://api.freebusy.io/beta/week/'
debugMode = True
secret_file = 'secret.data'

# user variables
userEmail = FM.load_data(secret_file)[0]
timeZone = 'America/New_York'


###############################################################################
# program functions
###############################################################################


# function that removes unicode characters
# helper function for shiftboard_parser
# copied from browser_handler
def utf8_encoder(unicoded_string):
    return unicoded_string.encode('utf-8')


# function that makes get request for data from a day
# returns json of the week as a dict
# _date is a datetime object
def get_calendar_data(_date, _user_email, _timezone='America/New_York'):
    # convert input date into busyfree format
    converted_date = _date.strftime("%Y-%m-%d")
    # make get request
    requestUrl = busyFreeAPI_url + _user_email + '?tz=' + _timezone + '&date=' + converted_date
    data = requests.get(requestUrl)
    # convert data to json then to a dict then return
    json_data = data.json()
    return json_data


# function that converts busyFree json to dict of date and timeslots
def get_timeslot_dict(dict_of_json_file):
    # empty dict used below
    dateTimeslots = {}
    # retrieve the days, days will be in a list
    _days = dict_of_json_file.get("days", [])
    # get date of each day and create date: timeslots dict
    for day in _days:
        # get date
        day_date = day.get("date", None)
        # get timeslots
        time_slots = day.get("timeslots", [])
        # add key and value to dict
        dateTimeslots[day_date] = time_slots
    # return final dict when done
    return dateTimeslots


# function to find available timeslots
# returns dict with date: list of (startTime, Endtime)
# dict shows free timeslots
# _participant is an email
def filter_out_busy_timeslots(_datetimeslot_dict, _participant):
        # dict to hold slotdates and slots
    final_dict = {}
    for key in _datetimeslot_dict:
        # get the timeslots in a list
        timeslot_list_of_dicts = _datetimeslot_dict[key]
        # variable to hold list of processed timeslots for just the day
        final_day_timeslot_list = []
        # check for participant list of dict
        for timeslot_dict in timeslot_list_of_dicts:
            participants_dict_list = timeslot_dict["participants"]
            # get participant dict
            for participant_dict in participants_dict_list:
                # get email value and isAvailable value and check if available
                if (participant_dict["email"] == _participant) and (participant_dict["isAvailable"]):
                    # get start time and end time
                    slotStartTime = timeslot_dict["startTime"]
                    slotEndTime = timeslot_dict["endTime"]
                    start_end_tuple = (slotStartTime, slotEndTime)
                    # populate list with timeslots for the day
                    final_day_timeslot_list.append(start_end_tuple)
                else:
                    pass  # ignore empty participant list
        # populate final dict with datetetime key and available timeslots value
        final_dict[key] = final_day_timeslot_list
    # return final dict when done
    return final_dict


# helper function that concatenates consecutive timeslots in a list
# see sample list in debugMode section at the End Of [this] File
def list_concat_consecutive_timeslots(input_list):
    tuple_list = input_list
    # print("here we go \n")
    # print(tuple_list)
    # compare end times to start time and concat recursively
    for x, y in zip(tuple_list, tuple_list[1:]):
        x_startime = x[0]
        x_endtime = x[1]
        y_starttime = y[0]
        y_endtime = y[1]

        if x_endtime == y_starttime:
            # take x_startime and y_endtime and make a tuple
            xy_tuple = (x_startime, y_endtime)
            # get index of x
            index_of_x = tuple_list.index(x)
            # remove x and y from tuple_list
            tuple_list.remove(x)
            tuple_list.remove(y)
            # insert xy_tuple where x used to be
            tuple_list.insert(index_of_x, xy_tuple)
            # recursively concatenate
            tuple_list = list_concat_consecutive_timeslots(tuple_list)
            break
        else:
            pass

    return tuple_list


# function to apply list_concat_consecutive_timeslots to the keys of availalble time slots
# changes available timeslots to continuous periods of time
# for sample free_time_dict see sample_free_time_dict
# outputs a a dict whose keys are list with long periods of time
def convert_timeslots_to_periods(free_time_dict):
    _output = free_time_dict
    for day in _output:
        # get timeslots of the day as a list
        tuple_list = _output[day]
        # convert the timeslot list to a period list and reassing value of dict
        _output[day] = list_concat_consecutive_timeslots(tuple_list)
    return _output


# function to convert google calendar time format to datetime object
# sample gtime_string u'2018-01-09T08:00:00-05:00'
def gtime_to_datetime_converter(gtime_unicoded_string):
    # remove unicode, ie unwanted 'u ' characters
    encoded_string = utf8_encoder(gtime_unicoded_string)
    #  encoded_string = gtime_unicoded_string  # skip encoding
    # get all but the six last characters
    gtime_date_and_time = encoded_string[:-6]
    # remove capital T
    gtime_date_and_time = gtime_date_and_time.replace("T", " ")
    # extract timezone
    # gtime_timezone = encoded_string[-6:]  # timezone for future use
    # parse gtime_date_and_time to datetime object sample: 2018-01-09 08:00:00
    parsed_datetime = datetime.strptime(gtime_date_and_time, '%Y-%m-%d %H:%M:%S')
    return parsed_datetime


# function that maps a function over a list of tuples
# tuple must have two values ie (x,y) not (x,y,z, ...)
def map_over_list_of_tuples(myfunc, tuple_list):
    # variable for output
    _output = []
    for x, y in tuple_list:
        # apply myfunc to x and y
        output_x = myfunc(x)
        output_y = myfunc(y)
        # make tuple and append to output list
        output_tuple = (output_x, output_y)
        _output.append(output_tuple)
    # return final list
    return _output


# function to convert all strings of a dict of periods into strings, including the keys
# function can convert any dict with unicoded strings for keys and values
# uses helper function gtime_to_datetime_converter
def dict_times_to_datetimes(unicoded_dict):
    # variable to hold output
    _output = unicoded_dict
    # find keys
    for key in _output.keys():
        # convert key to datetime
        new_key = gtime_to_datetime_converter(key)
        # get values, nb: values are lists of tuples
        dict_values = _output[key]
        # map over list and convert every element to make new value for dict
        list_new_value = map_over_list_of_tuples(gtime_to_datetime_converter, dict_values)
        # update dict key by poping old and adding new
        _output[new_key] = _output.pop(key)
        # use new key to update values
        _output[new_key] = list_new_value

    # return the output
    return _output


# function to get freetime schedule, should return list of free_periods
# takes datetime returns list of datetimes
# def retrieve_schedule_of_the_day(search_date)
# search_date can take any datetime but idealy should not have any minutes or seconds
def retrieve_schedule_of_the_day(search_date):
    # get data from calendar
    _retrieved_calendar_data = get_calendar_data(search_date, userEmail, timeZone)
    # get all the timeslots, converts json to dict
    _retrieved_timeslot_dict = get_timeslot_dict(_retrieved_calendar_data)
    # get just the free timeslots for given email
    _retrieved_free_timeslots = filter_out_busy_timeslots(_retrieved_timeslot_dict, userEmail)
    # combine consecutive 30 minute slots to longer periods
    _retrieved_free_periods = convert_timeslots_to_periods(_retrieved_free_timeslots)
    # convert all the dates in the dict to datetime objects
    _datetime_free_periods = dict_times_to_datetimes(_retrieved_free_periods)
    # extract just the date, date_to_tuple imported from scheduler
    _y, _m, _d = date_to_tuple(search_date)
    search_just_date = datetime(_y, _m, _d)
    # find free_periods for search_date and return as list
    return _datetime_free_periods[search_just_date]


# check if free function
# takes a tuple of datetimes and replies with bool
# takes tuple datetime of the querried range(timerange_datetime_tuple)
# and a list of tuples of the  free periods(tuple_list_free_periods), the tuples contain datetimes
def check_if_free_comparator(timerange_datetime_tuple, tuple_list_free_periods):
    # get startRange and endRange from input
    startRange = timerange_datetime_tuple[0]
    endRange = timerange_datetime_tuple[1]
    # check if free
    for startOfPeriod, endOfPeriod in tuple_list_free_periods:
        if (startOfPeriod <= startRange) and (endOfPeriod >= endRange):
            # you are free during this time period
            print(" You are free from " + startRange.strftime("%b %d %Y %I:%M %p") + " to " + endRange.strftime("%b %d %Y %I:%M %p"))
            return True
        else:
            pass  # keep searching through the list of tuples
    # if no matches have been found, return False
    print("No free time found for :" + startRange.strftime("%b %d %Y %I:%M %p") + "-" + endRange.strftime("%b %d %Y %I:%M %p"))
    return False


# Main entry point for the script.
def main():
    # troubleshooting
    if debugMode:
        requestDate = datetime(2018, 1, 12)
        # test if get_calendar_data works
        retrieved = get_calendar_data(requestDate, userEmail, timeZone)
        print("This is the retrieved data by get_calendar_data : \n")
        print(retrieved)
        # test get_timeslot_dict
        timeslotdict = get_timeslot_dict(retrieved)
        print("this is the dict with date: timeslot by get_timeslot_dict: \n")
        print(timeslotdict)

        # test if availalbe timeslot filter works
        availabletimes = filter_out_busy_timeslots(timeslotdict, userEmail)
        print("This is the filtered version: \n")
        print(availabletimes)

        # sample lists
        sample_list = [
            (u'2018-01-09T08:00:00-05:00', u'2018-01-09T08:30:00-05:00'),
            (u'2018-01-09T08:30:00-05:00', u'2018-01-09T09:00:00-05:00'),
            (u'2018-01-09T17:00:00-05:00', u'2018-01-09T17:30:00-05:00'),
            (u'2018-01-09T17:30:00-05:00', u'2018-01-09T18:00:00-05:00'),
            (u'2018-01-09T18:00:00-05:00', u'2018-01-09T18:30:00-05:00'),
            (u'2018-01-09T18:30:00-05:00', u'2018-01-09T19:00:00-05:00'),
            (u'2018-01-09T19:30:00-05:00', u'2018-01-09T20:00:00-05:00'),
        ]
        '''
        sample_list_two = [
            (u'2018-01-08T08:00:00-05:00', u'2018-01-08T08:30:00-05:00'),
            (u'2018-01-08T08:30:00-05:00', u'2018-01-08T09:00:00-05:00'),
            (u'2018-01-08T17:00:00-05:00', u'2018-01-08T17:30:00-05:00'),
            (u'2018-01-08T17:30:00-05:00', u'2018-01-08T18:00:00-05:00'),
            (u'2018-01-08T18:00:00-05:00', u'2018-01-08T18:30:00-05:00'),
            (u'2018-01-08T18:30:00-05:00', u'2018-01-08T19:00:00-05:00'),
            (u'2018-01-08T19:00:00-05:00', u'2018-01-08T19:30:00-05:00'),
            (u'2018-01-08T19:30:00-05:00', u'2018-01-08T20:00:00-05:00'),
            (u'2018-01-08T20:00:00-05:00', u'2018-01-08T20:30:00-05:00'),
            (u'2018-01-08T20:30:00-05:00', u'2018-01-08T21:00:00-05:00'),
            (u'2018-01-08T21:00:00-05:00', u'2018-01-08T21:30:00-05:00'),
            (u'2018-01-08T21:30:00-05:00', u'2018-01-08T22:00:00-05:00'),
        ]
        '''
        # test if list_concat_consecutive_timeslots works
        print("This is the UNCONCATENATED version of time list: \n")
        print(sample_list)
        print("This is the CONCATENATED version of time list: \n")
        print(list_concat_consecutive_timeslots(sample_list))

        # test if convert_timeslots_to_periods works
        converted_available_times = convert_timeslots_to_periods(availabletimes)
        print("This is the dict with periods, not timeslots (by convert_timeslots_to_periods): \n")
        print(converted_available_times)

        # test if gtime_to_datetime_converter works
        converted_datetime = gtime_to_datetime_converter(u'2018-01-09T19:30:00-05:00')
        print("This is the parsed google calendar date and time into datetime by gtime_to_datetime_converter")
        print(converted_datetime)
        print(type(converted_datetime))

        # test if map_over_list_of_tuples works
        print("Test of map_over_list_of_tuples, with list: [(1, 2), (3, 4)] : \n")
        print(map_over_list_of_tuples(str, [(1, 2), (3, 4)]))

        # test if dict_times_to_datetimes with dict of periods
        dict_converted_datetime = dict_times_to_datetimes(converted_available_times)
        print("This is a dict with parsed google calendar date times into datetime : \n")
        print(dict_converted_datetime)

        # sample data for check_if_free_comparator
        tuple_list_for_test = [
            (datetime(2018, 1, 8, 8, 0), datetime(2018, 1, 8, 9, 0)),
            (datetime(2018, 1, 8, 17, 0), datetime(2018, 1, 8, 22, 0))
        ]
        time_querry = (datetime(2018, 1, 8, 18, 0), datetime(2018, 1, 8, 19, 0))
        # test if check_if_free_comparator works using dict_converted_datetime
        print("This function check if you are free at from 8:30am to 9am on datetime(2018, 1, 8, 9, 0)")
        print(check_if_free_comparator(time_querry, tuple_list_for_test))

        # test retrieve schedule of the day with todays's date
        print("This is the schedule for the day entered by retrieve_schedule_of_the_day : \n")
        output_of_retrieve_schedule_of_the_day = retrieve_schedule_of_the_day(datetime(2018, 1, 22))
        print(output_of_retrieve_schedule_of_the_day)

        # test if check_if_free_comparator works with output_of_retrieve_schedule_of_the_day
        print("This is a test if output_of_retrieve_schedule_of_the_day work with check_if_free_comparator: \n")
        output_of_check_if_free_comparator = check_if_free_comparator(time_querry, output_of_retrieve_schedule_of_the_day)
        print(output_of_check_if_free_comparator)

    else:
        pass  # not in debugMode


if __name__ == '__main__':
    main()
