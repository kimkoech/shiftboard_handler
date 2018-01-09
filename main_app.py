###############################################################################
"""
Program that grabs shifts from shiftboard
Uses functions defined in the browser_handler module

Mru:
Jan 8th 2018    - started implementing calendar mode
                - imported calendar_manager
"""
###############################################################################
# import modules
from datetime import datetime, timedelta
import browser_handler as BH  # local module for browser control
import scheduler as SC  # local module for schedule
import file_manager as FM  # local mdule with file funcions
import spinning_cursor as SPC  # local module with spinner
import calendar_manager as CLDM  # local module with calendar API


# program variables
debugMode = False
weekNo = 2
takenShifts = 'taken_shifts.txt'
wakeHour = 9  # am
wakeMinute = 35  # am
calendarMode = True
dailyShiftStore = 'daily_shift_store.txt'
secret_data = 'secret.data'

# user variables
email = FM.load_data(secret_data)[0]  # get
password = FM.load_data(secret_data)[1]
address = 'https://www.shiftboard.com/log-in/'  # shiftboard website address


# shift related variables
desiredShifts = SC.desiredShifts  # shifts to grab
LAMONT = 'Lab Assistance - Lamont'
CABOT = 'CABOT Studios'

# troubleshooting variables for tests
if debugMode:
        # change variable to desired shift test time
    fridayShift = datetime(2018, 01, 27, 20)
else:
    pass


# Main entry point for the script.
def main():

    # variable to hold dersied shifts start times in a list
    shiftsOfTheDay = []
    # check the mode (calendar mode or scheduler mode)
    if calendarMode:

        # check if record of shifts already exists in file, check date timestamp
        storedData = FM.load_data(dailyShiftStore)
        timestamp_storedData = storedData[0]  # never use index with an empty tuple
        if (timestamp_storedData == SC.today_raw_date()):

            # data already exists thus retrieve shifts of the day ie index 1 of tuple
            print("Valid up-to-date shift data found in storage")
            shiftsOfTheDay = storedData[1]
            print("Storage data retrieved!")

        else:  # get new data and write to file
            # initiation sequence
            print("Calendar mode active. \nRetrieving data from shiftboard website")
            BH.launch_browser(address)  # go to shiftbaord website
            BH.login(email, password)  # login
            BH.goto_next_week(weekNo)  # go to weekNo weeks ahead
            # extract table data from shiftboard
            parsedShiftboardTable_for_calendar = BH.shiftboard_parser(BH.tableRowXpath)
            # extract day's shifts in a list of tuples
            extractedDayShifts = BH.extract_day_shift_time(parsedShiftboardTable_for_calendar, weekNo)
            # convert shift time ranges to datetimes and get list of tuples of shifts
            tuple_of_date_and_shift_tuples = BH.shift_time_to_datetime_parser(extractedDayShifts)
            list_of_tuples_shift_times_of_day = tuple_of_date_and_shift_tuples[1]  # list of shifts for this day
            # use calendar_manager functions to retrieve day schedule with free periods
            print("Extracting schedule data from calendar")
            search_date = tuple_of_date_and_shift_tuples[0]  # get date on tuple list of extractedDayShifts
            list_free_periods = CLDM.retrieve_schedule_of_the_day(search_date)  # list of free periods for this day
            # use calendar_manager functions to compare shift time to free periods
            for each_shift in list_of_tuples_shift_times_of_day:
                # check if free at shift times and add start times of shifts that work to shiftsOfTheDay
                isFree = CLDM.check_if_free_comparator(each_shift, list_free_periods)
                if isFree:
                    # store start times of each shift to shiftsOfTheDay list.
                    shiftsOfTheDay.append(each_shift[0])

                else:
                    pass  # do nothing
            # remove duplicates from shiftsOfTheDay, also changes order of elements ie sets are unordered
            print("List of shifts compiled successfully")
            shiftsOfTheDay = list(set(shiftsOfTheDay))
            # store to file for future sessions, include datestamp stored in dailyShiftStore
            print("Writing list of shifts to storage file...")
            FM.write_data(dailyShiftStore, (SC.today_raw_date(), shiftsOfTheDay))
            print("Stored successfully")

    else:

        # schedule mode
        # get list of dates of desired shifts two weeks from now from scheduler
        shiftsOfTheDay = SC.get_desired_shift_dates(desiredShifts, weekNo)

    # remove confirmed shifts before looping
    for confirmed_time in FM.retrieve_datetime_from_file(takenShifts):
        # check if shift in list
        if confirmed_time in shiftsOfTheDay:
            shiftsOfTheDay.remove(confirmed_time)
            print("Removing confirmed time: " + str(confirmed_time) + " from list")
        else:  # else clear file, ie start of a new day
            FM.clear_file(takenShifts)
            print("Taken shifts file cleared")

    # switch to shift listening mode
    print("listening for shifts...")

    # Make the program loop forever
    while True:

        # get approaching shift two weeks from now, (30 seconds earlier)
        shiftToTake = SC.check_if_shift_approching(shiftsOfTheDay, weekNo, 30)

        # check if its sleeping time
        if SC.today_time(wakeHour, wakeMinute) > datetime.now():
            # go to sleep
            print("sleeping time zzz")
            break

        # check if desired shifts is empty
        elif shiftsOfTheDay == []:
            # exit loop if empty
            if calendarMode:
                print("You have no free periods today, or there are no more shifts available today")
            else:
                print("Your schedule is empty today")
            # exit
            break

        # check if shift is approaching
        elif shiftToTake is None:

            # keep waiting for shift to approach
            SPC.spinner()

        # run the code below if approaching
        else:

            # launch browser
            BH.launch_browser(address)

            # enter username and password and log in
            BH.login(email, password)

            # go to two weeks ahead
            BH.goto_next_week(weekNo)

            # parse shiftboard table
            parsedShiftboardTable = BH.shiftboard_parser(BH.tableRowXpath)

            # get shift confirm button
            confirmBtn = BH.grab_shift(shiftToTake, parsedShiftboardTable, LAMONT)

            # confirm shift, wait until 1 second before time
            while (datetime.now() + timedelta(weeks=weekNo)) < (shiftToTake - timedelta(seconds=1)):
                pass
            # confirm
            BH.confirm_shift(confirmBtn)

            # remove confirmed shift from list for this session and record to file
            shiftsOfTheDay.remove(shiftToTake)
            FM.update_file(takenShifts, shiftToTake)  # record to file, for future sessions

            # switch to shift listening mode mode once done
            print("Done.\nListening for shifts...")
            # BH.delay(5)
            # BH.exit_sequence()

    # print loop exit message
    timestamp = datetime.now()
    print("loop exit at :" + timestamp.strftime("%b %d %Y %I:%M:%S %p"))

    # set arbitrary variable for wakeTime, value will be updated below
    wakeTime = timestamp
    # find wake up time by increasing timestamp by 1 day, fix this with if statements
    if SC.today_time(wakeHour, wakeMinute) < datetime.now() < SC.today_time(23, 59):
        wakeTime = timestamp + timedelta(days=1)
    else:
        pass  # dont add a day ie wake up in the morning the same day

    # extract current date from wakeTime
    wakeTime_year, wakeTime_month, wakeTime_day = SC.date_to_tuple(wakeTime)
    # date at 8:45am on the next day
    wakeTime = datetime(wakeTime_year, wakeTime_month, wakeTime_day, wakeHour, wakeMinute)
    # activate sleepmode and wait until 8:45am the next day to wake
    print ("sleep mode activated at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
    # uncomment when ready to commence
    while datetime.now() < wakeTime:
        pass  # stay in sleep mode
    # wake up sequence
    print("sleep mode deactivated. Waking up at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
    FM.clear_file(takenShifts)  # clear file that holds taken shifts
    main()  # call main to wake the program and listen for shifts


if __name__ == '__main__':
    main()
