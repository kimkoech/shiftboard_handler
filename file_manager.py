###############################################################################
"""
Program to manage shift file for shiftboard program

Created by:	skeleton by Billy Koech
Date:		Jan 4th 2018

mru(most recent update):

"""
###############################################################################
# import modules
from datetime import datetime

# program variables
debugMode = False  # troubleshooting

# user variables
if debugMode:
    takenShiftFile = 'taken_shifts.txt'
else:
    pass

###############################################################################
# program functions
###############################################################################


# function to update data in a file
def update_file(file_name, data):
    file = open(file_name, "a")
    file.write(data + "\n")
    file.close()


# function to erase data in file
def clear_file(file_name):
    open(file_name, "w").close()


# function to read lines in file
# return list of times
def get_lines(file_name):
    file = open(file_name, "r")
    return file.readlines()


# function to convert datetimes strings datetimes
def string_to_datetime(_string):
    return datetime.strptime(str(_string), '%Y-%m-%d %H:%M:%S')


# function to remove \n character from list
def remove_extras(_list):
    new_list = []
    for el in _list:
        new_list.append(el.rstrip().rstrip())
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


# Main entry point for the script.
def main():
    if debugMode:
        data = str(datetime(2017, 1, 26, 9))
        clear_file(takenShiftFile)
        update_file(takenShiftFile, data)
        new = retrieve_datetime_from_file(takenShiftFile)
        print(new)

    else:
        pass


if __name__ == '__main__':
    main()
