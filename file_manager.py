###############################################################################
"""
Program to manage shift file for shiftboard program

Created by: skeleton by Billy Koech
Date:       Jan 4th 2018

mru(most recent update):
Jan 8th 2018    - deleted one of the .rstrip() from remove_extras
                - added write_non_string_data function
                - added print statements to start_log() and stop_log()

"""
###############################################################################
# import modules
from datetime import datetime
import pickle  # module for writing non-string data to files
import sys  # module to print to log file

# program variables
debugMode = False  # troubleshooting
recordMode = (not debugMode)  # mode for using this module to write to file
ORIG_STDOUT = sys.stdout
logfile = 'logfile.log'
recordFile = 'record_file.txt'
takenShiftFile = 'taken_shifts.txt'
dailyShiftStore = 'daily_shift_store.txt'
secret_file = 'secret.data'

logger = open(logfile, 'a')

# user variables
if debugMode:
    pass
else:
    pass

###############################################################################
# program functions
###############################################################################


# function to update data in a file


def update_file(file_name, data):
    file = open(file_name, "a")
    file.write(str(data) + "\n")
    file.close()


# function to erase data in file
def clear_file(file_name):
    open(file_name, "w").close()


# function to read lines in file
# return list of times
def get_lines(file_name):
    file = open(file_name, "r")
    _data = file.readlines()
    file.close()
    return _data


# function to convert datetimes strings datetimes
def string_to_datetime(_string):
    return datetime.strptime(str(_string), '%Y-%m-%d %H:%M:%S')


# function to remove \n character from list
def remove_extras(_list):
    new_list = []
    for el in _list:
        new_list.append(el.rstrip())
    return new_list


# function to return datetime list from file
def retrieve_datetime_from_file(file_name):
    # get the lines
    lines = get_lines(file_name)
    # remove unecessary characters
    lines = remove_extras(lines)
    # convert to datetime list and return
    lines = map(string_to_datetime, lines)
    return lines


# function to write non-string data to a file
# overwrites file every time
def write_data(file_name, _data):
    my_file = open(file_name, "w")
    pickle.dump(_data, my_file)
    my_file.close()


# function to load non-string data from a file
# raises EOFError if file is empty
def load_data(file_name):
    my_file = open(file_name, "r")
    _output = pickle.load(my_file)
    return _output


# function to clear data file
def clear_data_file(file_name):
    open(file_name, "w").close()


# function to append data to a file
def append_data(file_name, _data):
    my_file = open(file_name, "a")
    pickle.dump(_data, my_file)
    my_file.close()


# function to retrieve objects from data file
# returns a list of objects in file
def data_file_to_list(file_name):
    my_file = open(file_name, "r")
    objs = []
    while True:
        try:
            objs.append(pickle.load(my_file))
        except EOFError:
            break
    return objs


# function to redirect print statement to a log file
def start_log():
    print("Log mode active. Redirecting ouput to logfile")
    sys.stdout = logger
    print("\n New log session : " + datetime.now().strftime("%b %d %Y %I:%M:%S %p") + "\n")

# function to turn of logging


def stop_log():
    print("\n End of log session : " + datetime.now().strftime("%b %d %Y %I:%M:%S %p") + "\n")
    sys.stdout = ORIG_STDOUT
    print("Log mode deactivated : " + datetime.now().strftime("%b %d %Y %I:%M:%S %p") + "\n")
    logger.close()


# Main entry point for the script.
def main():
    start_log()
    if debugMode:

        # data = datetime(2017, 1, 26, 9)
        clear_file(takenShiftFile)
        # update_file(takenShiftFile, data)
        data1 = datetime(2018, 1, 23, 9)
        # data2 = datetime(2018, 1, 22, 11)
        # data3 = datetime(2018, 1, 22, 13)
        # data4 = datetime(2018, 1, 22, 14)
        # data5 = datetime(2018, 1, 22, 15)
        # data6 = datetime(2018, 1, 22, 18)
        # data7 = datetime(2018, 1, 22, 20)
        update_file(takenShiftFile, data1)
        # update_file(takenShiftFile, data2)
        # update_file(takenShiftFile, data3)
        # update_file(takenShiftFile, data4)
        # update_file(takenShiftFile, data5)
        # update_file(takenShiftFile, data6)
        # update_file(takenShiftFile, data7)
        new = retrieve_datetime_from_file(takenShiftFile)
        print(new)
        print(get_lines(takenShiftFile))

        # test for write non_string data
        sample = [
            (u'2018-01-09T08:00:00-05:00', u'2018-01-09T08:30:00-05:00'),
            (u'2018-01-09T08:30:00-05:00', u'2018-01-09T09:00:00-05:00'),
            (u'2018-01-09T17:00:00-05:00', u'2018-01-09T17:30:00-05:00'),
            (u'2018-01-09T17:30:00-05:00', u'2018-01-09T18:00:00-05:00'),
            (u'2018-01-09T18:00:00-05:00', u'2018-01-09T18:30:00-05:00'),
            (u'2018-01-09T18:30:00-05:00', u'2018-01-09T19:00:00-05:00'),
            (u'2018-01-09T19:00:00-05:00', u'2018-01-09T19:30:00-05:00'),
            (u'2018-01-09T19:30:00-05:00', u'2018-01-09T20:00:00-05:00'),
        ]
        # uncomment when you want to write to dailyShiftStore
        # write_data(dailyShiftStore, (datetime(2018, 1, 7), sample))

        # test for load non string data
        output_of_load_data = load_data(dailyShiftStore)
        print(" This is output_of_load_data by load_data: \n")
        print(output_of_load_data)
        # clear data when done debugging
        # clear_data_file(dailyShiftStore)

    else:
        pass

    stop_log()
    if recordMode:
        # clear shift file and add custom data
        clear_data_file(takenShiftFile)
        test_tuple = (datetime(2018, 1, 23, 11), datetime(2018, 1, 23, 12))
        test_tuple2 = (datetime(2018, 1, 23, 12), datetime(2018, 1, 23, 13))
        append_data(takenShiftFile, test_tuple)
        append_data(takenShiftFile, test_tuple2)
        print("Printing data from " + takenShiftFile + " by data_file_to_list \n")
        print(data_file_to_list(takenShiftFile))

        # clear dailyShiftStore and attemp to to open
        print("\n Content in daily shift store : " + dailyShiftStore + "\n")
        # clear_data_file(dailyShiftStore)
        print(load_data(dailyShiftStore))
    else:
        pass


if __name__ == '__main__':
    main()
