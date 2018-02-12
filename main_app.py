###############################################################################
"""
Program that grabs shifts from shiftboard
Uses functions defined in the browser_handler module

Mru:
Jan 8th 2018    - started implementing calendar mode
                - imported calendar_manager
                - replaced file_manager functions from  clear_file to clear_data_file
                                                        update_file to append_data
                                                        retrieve_datetime_from_file to append_data
"""
###############################################################################
# import modules
from datetime import datetime, timedelta
import browser_handler as BH  # local module for browser control
import scheduler as SC  # local module for schedule
import file_manager as FM  # local mdule with file funcions
# import spinning_cursor as SPC  # local module with spinner
import calendar_manager as CLDM  # local module with calendar API
import sys  # module to get input from user
import stdout_GUI as GUI  # gui for display
# from tkMessageBox import askyesno  # uncomment if switching to alternative input method


# program variables
debugMode = False
weekNo = 2
takenShifts = 'taken_shifts.txt'
wakeHour = 8  # am
wakeMinute = 50  # am
calendarMode = True
dailyShiftStore = 'daily_shift_store.txt'
secret_data = 'secret.data'
FirstTimeInitiating = True

# user variables
email = FM.load_data(secret_data)[0]  # get email from file
password = FM.load_data(secret_data)[1]  # get password from file
address = 'https://www.shiftboard.com/log-in/'  # shiftboard website address


# shift related variables
desiredShifts = SC.desiredShifts  # shifts to grab
LAMONT = 'LAMONT'
CABOT = 'CABOT Studios'
LOCATION = LAMONT

# program functions


# fuction to remove shift from shift list and update storage file
def shift_remover(_shift_to_remove, list_of_shifts):
    list_of_shifts.remove(_shift_to_remove)
    FM.write_data(dailyShiftStore, (SC.today_raw_date(), list_of_shifts))  # update shift store file
    print("Shift records updated, " + SC.datetime_tuple_to_string_format(_shift_to_remove) + " removed from listening list")


# troubleshooting variables for tests
if debugMode:
        # change variable to desired shift test time
    fridayShift = datetime(2018, 01, 27, 20)
else:
    pass


# Main entry point for the script.
def main_x():
    # startup message
    global FirstTimeInitiating
    if (FirstTimeInitiating):
        print("Program initiated on " + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
        FirstTimeInitiating = False
    else:
        pass

    # get user input
    try:
        # Update storage file?
        if sys.argv[1].strip().lower() == 'yes':
            print("Clear command received, clearing storage file...")
            FM.clear_data_file(dailyShiftStore)
            print("Storage file cleared successfully")
            sys.argv = []  # clear input
        else:
            pass
    except IndexError:
        pass  # ignore this error

    '''
    # Alternative code for requesting user input

    global FirstTimeInitiating
    if FirstTimeInitiating:
        if askyesno('Verify', 'Update storage data?'):
            print("Clear command received, clearing storage file...")
            FM.clear_data_file(dailyShiftStore)
            print("Storage file cleared successfully")
            FirstTimeInitiating = False
        else:
            pass  # ignore
    else:
        pass  # ignore
    '''

    # variable to hold dersied shifts start times in a list
    shiftsOfTheDay = []
    # check the mode (calendar mode or scheduler mode)
    if calendarMode:

        # check if record of shifts already exists in file, check date timestamp
        timestamp_storedData = None  # variable to hold timestamp from stored file
        try:
            storedData = FM.load_data(dailyShiftStore)
            timestamp_storedData = storedData[0]  # never use index with an empty tuple
        except EOFError:
            pass  # do not alter value of timestamp stored data
        if (timestamp_storedData == SC.today_raw_date()):

            # data already exists thus retrieve shifts of the day ie index 1 of tuple
            print("Valid up-to-date shift data found in storage")
            shiftsOfTheDay = storedData[1]
            print("Storage data retrieved!")

        else:  # get new data and write to file
            GUI.BAR_MODE = "loading"
            # initiation sequence
            print("Calendar mode active. \nRetrieving data from shiftboard website")
            BH.launch_browser(address)  # go to shiftbaord website
            BH.login(email, password)  # login
            BH.goto_next_week(weekNo)  # go to weekNo weeks ahead
            # extract table data from shiftboard
            parsedShiftboardTable_for_calendar = BH.shiftboard_parser(BH.tableRowXpath)
            # remove taken shifts
            parsedShiftboardTable_for_calendar = BH.remove_taken_shifts(parsedShiftboardTable_for_calendar)
            print("Shift filtering complete")
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
                    # store start time and end times of each shift to shiftsOfTheDay list.
                    shiftsOfTheDay.append(each_shift)

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

    # switch to shift listening mode and enter loop
    print("Listening for shifts from " + LOCATION + "...")
    GUI.BAR_MODE = "listening"  # switch display mode

    # Make the program loop forever
    while True:

        # get approaching shift two weeks from now, (30 seconds earlier)
        shiftToTake = SC.check_if_shift_approching(shiftsOfTheDay, weekNo, 30)

        # if exit button is pressed in GUI
        if GUI.exit_thread:
            break

        # check if its sleeping time
        elif SC.today_time(wakeHour, wakeMinute) > datetime.now():
            # go to sleep
            print("Sleeping time zzz")
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
            pass
            # SPC.spinner()

        # run the code below if approaching
        else:
            # GUI
            GUI.BAR_MODE = "loading"

            # wait for internet connectivity
            print("Checking for internet connectivity at " + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
            while (not BH.connected()):
                # check if program has been aborted
                if GUI.exit_thread:
                    break
                else:
                    pass  # keep waiting for internet connectivity

            # connection successful
            print("Internet connection established at " + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))

            # launch browser
            BH.launch_browser(address)

            # enter username and password and log in
            BH.login(email, password)

            # go to two weeks ahead
            BH.goto_next_week(weekNo)

            # parse shiftboard table
            parsedShiftboardTable = BH.shiftboard_parser(BH.tableRowXpath)

            # remove taken shifts
            parsedShiftboardTable = BH.remove_taken_shifts(parsedShiftboardTable)

            # get shift confirm button
            confirmBtn = BH.grab_shift(shiftToTake, parsedShiftboardTable, LOCATION)

            # check if get shift confirm button is empty
            if confirmBtn is None:
                # remove shift time from list and update record to file
                print("Could NOT find shift on shiftboard")
                shift_remover(shiftToTake, shiftsOfTheDay)
                # then call main
                main_x()
            else:
                pass  # ignore if shift found

            # create function to abort shift grabbing if need be
            def abort_grabbing():
                shift_remover(shiftToTake, shiftsOfTheDay)  # remove shift
                main_x()  # call main to abort

            # abort message
            ABORT_MESSAGE = SC.datetime_tuple_to_string_format(shiftToTake) + '''\nThis shift will be taken in less than 30 seconds. Click below to cancel'''

            # confirm shift, wait until the time reaches
            GUI.BAR_MODE = "flashing"  # change bar GUI

            # ask user if shift grabbing should be aborted
            GUI.final_shift_notification(15000, ABORT_MESSAGE, abort_grabbing)

            while ((datetime.now() + timedelta(weeks=weekNo)) < (shiftToTake[0]) + timedelta(milliseconds=1)):
                # check if program has been aborted
                if GUI.exit_thread:
                    break
                else:
                    pass  # ignore

            # confirm
            BH.confirm_shift(confirmBtn)
            GUI.BAR_MODE = "loading"

            # remove confirmed shift from list for this session and record to file
            shift_remover(shiftToTake, shiftsOfTheDay)

            # switch to shift listening mode mode once done
            print("Done.\nListening for shifts from " + LOCATION + "...")
            GUI.BAR_MODE = "listening"
            # BH.delay(5)
            # BH.exit_sequence()
        BH.delay(1)  # delay for 1 second, decrease CPU cycle rate

    # print loop exit message
    timestamp = datetime.now()
    print("Loop exit at :" + timestamp.strftime("%b %d %Y %I:%M:%S %p"))

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
    if not GUI.exit_thread:
        print ("Sleep mode activated at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
        GUI.BAR_MODE = "sleeping"
    # uncomment when ready to commence
    while datetime.now() < wakeTime:
        # if exit button pressed
        if GUI.exit_thread:
            BH.exit_sequence()
            GUI.exit_success = True  # indicate to GUI that exit was successful
            quit()  # exit all python scripts
            break
        else:
            GUI.gray_fade_in()
            GUI.gray_fade_out()
        BH.delay(3)  # decrease CPU cycle rate by sleeeping
    # if exit button NOT pressed
    if not GUI.exit_thread:
        # wake up sequence
        print("Sleep mode deactivated. Waking up at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
        GUI.BAR_MODE = "listening"
        main_x()  # call main to wake the program and listen for shifts
    else:
        pass


def main():
    GUI.display(main_x)


if __name__ == '__main__':
    main()
