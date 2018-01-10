###############################################################################
"""
Program to redirect output of stdout to GUI
based on K-DawG007's code:

Written by K-DawG007
My SO profile: http://stackoverflow.com/users/2425215/k-dawg


Skeleton Created  Billy Koech
Date:       Jan 4th 2018

mru(most recent update):

Jan 9 2018 - Added K-DawG007's redirect code
"""
###############################################################################
# import modules
import Tkinter as Tk
import sys
import threading
# program variables
ORIG_STDOUT = sys.stdout

# user variables

###############################################################################
# program functions
###############################################################################

root = Tk.Tk()
text = Tk.Text(root)
text.pack()

exit_thread = False
exit_success = False


class Std_redirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        if not exit_thread:
            self.widget.insert(Tk.END, string)
            self.widget.see(Tk.END)

    def flush(self):
        pass


def stop_thread():
    global exit_thread
    exit_thread = True
    root.destroy()
    sys.stdout = ORIG_STDOUT

# test function for the output


def gen():
    x = 0
    while not exit_thread:
        yield x
        x += 1
    global exit_success
    exit_success = True


def call_gen():
    for i in gen():
        print i


def display(myfunc):
    exit_button = Tk.Button(root, text='Exit', command=stop_thread)
    exit_button.pack()

    sys.stdout = Std_redirector(text)

    thread1 = threading.Thread(target=myfunc)
    thread1.start()

    root.mainloop()


# display(call_gen)
