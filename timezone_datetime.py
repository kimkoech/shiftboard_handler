###############################################################################
"""
Program description

Created by:	skeleton by Billy Koech
Date:		Jan 4th 2018

mru(most recent update):

"""
###############################################################################
# import modules
from datetime import datetime, timedelta

# program variables
debugMode = False
timeDifference = 0
addition = False
# user variables

###############################################################################
# program functions
###############################################################################


# fuction to return time in a different time zone
def now(time_difference=timeDifference, operation=addition):
    if addition:
        return datetime.now() + timedelta(hours=time_difference)
    else:
        return datetime.now() - timedelta(hours=time_difference)


# Main entry point for the script.
def main():
    # troubleshooting
    if debugMode:
        print(now())
    else:
        pass  # do nothing


if __name__ == '__main__':
    main()
