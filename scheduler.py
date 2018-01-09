###############################################################################
"""
Program that generated schedule of desired shifts
call get_desired_shift_dates() with a dict and an int to generate a
schedule in the form of a list of datetimes

Created by: skeleton by Billy Koech
Date:       Jan 4th 2018

mru(most recent update):
Jan 7th 2018 - added today_time

"""
###############################################################################
# import modules
from datetime import datetime, timedelta

# program variables
shifts_list = []  # list with dates and times formated in datetime format
debugMode = False

# user variables

# enter your shift times here in 24 Hour format:
desiredShifts = {'Sun': [],
                 'Mon': [(9, 11)],
                 'Tue': [],
                 'Wed': [],
                 'Thu': [(9, 11), (14, 15)],
                 'Fri': [(9, 11), (20, 22)],
                 'Sat': []}  # regular shifts to be grabbed

###############################################################################
# program functions
###############################################################################


# function that converts date to tuple
def date_to_tuple(date_and_time):
    bare_year, bare_month, bare_day = date_and_time.strftime("%Y/%m/%d").split("/")
    return (int(bare_year), int(bare_month), int(bare_day))


# function that returns today's raw date
def today_raw_date():
    _y, _m, _d = date_to_tuple(datetime.now())
    return datetime(_y, _m, _d)


# function that takes time and creates datetime of today
def today_time(_hour, _minute):
    _year, _month, _day = date_to_tuple(datetime.now())
    return datetime(_year, _month, _day, _hour, _minute)


# function to get dates of desired shifts delta weeks from now
# returns list of datetimes, returns just the start times
def get_desired_shift_dates(schedule_dict, delta):
    # get time now
    timeNow = datetime.now()
    # add delta weeks to date
    desiredWeekday = timeNow + timedelta(weeks=delta)  # adds delta weeks
    # get year, month and day for desiredWeekday
    dateTuple = date_to_tuple(desiredWeekday)
    desired_year = dateTuple[0]
    desired_month = dateTuple[1]
    desired_day = dateTuple[2]
    # convert desiredWeekday to weekday string format and find shift times in schedule
    weekdayFormat = desiredWeekday.strftime("%a")
    shifts_of_the_day = schedule_dict[weekdayFormat]  # this is a list of tuples
    # find start and end times in shift times
    for startTime, endTime in shifts_of_the_day:
        # make shift list in datetime format, include just the startTime
        shifts_list.append(datetime(desired_year, desired_month, desired_day, startTime))

    return shifts_list


# function that compares list datetimes to time x weeks ahead
# constraint: we can only grab shifts two weeks ahead of time in shiftboard
# decrease_delta decreases times in list by seconds
def check_if_shift_approching(schedule_list, delta, decrease_delta):
    for time in schedule_list:
        if (datetime.now() + timedelta(weeks=delta)) >= (time - timedelta(seconds=decrease_delta)):
            time_on_this_date = (timedelta(weeks=delta) + datetime.now())
            print("Grabbing time approaching E.A.T. = " + str(time - time_on_this_date))
            return time
        else:
            # troubleshooting
            if debugMode:
                print("...")
            else:
                pass
    return None


# Main entry point for the script.
# run test codes here
def main():
    # troubleshhoting
    if debugMode:
        # get shift list for a day like this two weeks from now
        shifts = get_desired_shift_dates(desiredShifts, 2)
        print("shift list: ", shifts)
        # print formated shift list
        print("formated shift list:")
        for _shift in shifts:
            print(_shift.strftime("%b %d %Y %I:%M:%S %p"))

        # compare desired shifts to time
        approachingShift = check_if_shift_approching(shifts, 2, 5)
        print("approaching shift: ", approachingShift)

        # test today time
        # datetime at 8am today will be:
        print(today_time(8, 0))
    else:
        pass


if __name__ == '__main__':
    main()
