import itertools  # for spinner 1
import sys  # for spinner 1 and 2
import time  # for spinner 2
from file_manager import start_log, stop_log


# variables
chars = itertools.cycle(['-', '/', '|', '\\'])
debugMode = True  # troubleshooting


# spinner 1 funcion
# based on function from stackoverflow
# https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor-using-python
# requires while loop
def spinner():
    sys.stdout.write(next(chars))  # write the next character
    sys.stdout.flush()                # flush stdout buffer (actual character display)
    sys.stdout.write('\b')            # erase the last written char


# spinner 2 function
# based on function from stackoverflow
# https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor-using-python
# does not require while loop
def slow_spinner():
    print ("processing...\\")
    syms = ['\\', '|', '/', '-']

    for _ in range(10):
        for sym in syms:
            sys.stdout.write("\b%s" % sym)
            sys.stdout.flush()
            time.sleep(.5)


# Main entry point for the script.
def main():
    start_log()
    stop_log()
    if debugMode:
        while True:
            spinner()

    else:
        pass


if __name__ == '__main__':
    main()
