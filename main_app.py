###############################################################################
"""
Program that grabs shifts from shiftboard
Uses functions defined in the browser_handler module
"""
###############################################################################
# import modules
from datetime import datetime, timedelta
import browser_handler as BH  # local module for browser control
import scheduler as SC  # local module for schedule
import file_manager as FM  # local mdule with file funcions
import spinning_cursor as SPC  # local module with spinner


# program variables
debugMode = False
weekNo = 3
takenShifts = 'taken_shifts.txt'

# user variables
email = ''
password = ''
address = 'https://www.shiftboard.com/log-in/'  # shiftboard website address

# shift(s) to grab
desiredShifts = SC.desiredShifts


# troubleshooting variables for tests
if debugMode:
        # change variable to desired shift test time
    fridayShift = datetime(2018, 01, 27, 20)
else:
    pass


# Main entry point for the script.
def main():

    # get list of dates of desired shifts two weeks from now
    shiftsOfTheDay = SC.get_desired_shift_dates(desiredShifts, weekNo)

    # remove confirmed shifts before looping
    for confirmed_time in FM.retrieve_datetime_from_file(takenShifts):
        shiftsOfTheDay.remove(confirmed_time)

    # switch to shift listening mode
    print("listening for shifts...")

    # Make the program loop forever
    while True:

        # get approaching shift two weeks from now, (30 seconds earlier)
        shiftToTake = SC.check_if_shift_approching(shiftsOfTheDay, weekNo, 30)

        # check if desired shifts is empty
        if shiftsOfTheDay == []:
            # exit loop if empty
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

            # get shift confirm button, # unused - replace _ with shift datetime
            confirmBtn = BH.grab_shift(shiftToTake)

            # confirm shift, wait until 1 second before time
            while (datetime.now() + timedelta(weeks=weekNo)) < (shiftToTake - timedelta(seconds=1)):
                pass
            # confirm
            BH.confirm_shift(confirmBtn)

            # remove confirmed shift from list and record to file
            shiftsOfTheDay.remove(shiftToTake)
            FM.update_file(takenShifts, shiftToTake)

            # switch to shift listening mode mode once done done
            print("Done.\nListening for shifts...")
            # BH.delay(5)
            # BH.exit_sequence()

    # print loop exit message
    timestamp = datetime.now()
    print("loop exit at :" + timestamp.strftime("%b %d %Y %I:%M:%S %p"))

    # find wake up time by increasing timestamp by 1 day
    wakeTime = timestamp + timedelta(days=1)
    # extract current date from wakeTime
    wakeTime_year, wakeTime_month, wakeTime_day = SC.date_to_tuple(wakeTime)
    # date at 8:45am on the next day
    wakeTime = datetime(wakeTime_year, wakeTime_month, wakeTime_day, 8, 45)
    # activate sleepmode and wait until 8:45am the next day to wake
    print ("sleep mode activated at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
    while datetime.now() < wakeTime:
        pass  # stay in sleep mode
    # wake up sequence
    print("sleep mode deactivated. Waking up at :" + datetime.now().strftime("%b %d %Y %I:%M:%S %p"))
    FM.clear_file(takenShifts)  # clear file that holds taken shifts
    main()  # call main to wake the program and listen for shifts


if __name__ == '__main__':
    main()
