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
import file_manager as FM
import time  # module used by bouncing ball
from random import randint  # module with random int generator
from all_colors import COLORS
# program variables
ORIG_STDOUT = sys.stdout
logfile = 'logfile.log'

# user variables

###############################################################################
# program functions and classes
###############################################################################

###############################################################################
# SECTION 1: Written by K-DawG007
# http://stackoverflow.com/users/2425215/k-dawg
###############################################################################

root = Tk.Tk()
text = Tk.Text(root, height=7)
text.config(foreground='green', background='gray1', borderwidth=0, highlightthickness=0)
root.geometry("500x140")
root.config(background='gray1')
root.title('Shiftboard Handler')
text.pack()


exit_thread = False
exit_success = False


class Std_redirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        if not exit_thread:
            FM.GUI_log(logfile, string)
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

###############################################################################
# SECTION 2: Bouncing Ball Written by sheldonzy
# modified into a loading bar by Billy Koech
# https://codereview.stackexchange.com/questions/175813/python-tkinter-bouncing-ball-animation
###############################################################################


WIDTH = 500
HEIGHT = 10
SIZE = 500
OFFSET = 550
canvas = Tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='gray1', highlightthickness=0)
canvas.pack()
color = 'green'


class Bar:
    def __init__(self):
        self.shape = canvas.create_rectangle(0, 0, SIZE, SIZE, fill=color)
        self.speedx = 5  # changed from 3 to 9
        self.speedy = 0  # changed from 3 to 9
        self.active = True
        self.move_active()

    def bar_update(self):
        canvas.move(self.shape, self.speedx, self.speedy)
        pos = canvas.coords(self.shape)
        if pos[2] - OFFSET >= WIDTH or pos[0] <= - OFFSET:
            self.speedx *= -1
        if pos[3] >= HEIGHT or pos[1] <= 0:
            self.speedy *= -1

    def move_active(self):
        if self.active:
            self.bar_update()
            root.after(15, self.move_active)  # changed from 10ms to 30ms


##########


def display(myfunc):
    exit_button = Tk.Button(root, text='Exit', command=stop_thread, pady=0, padx=0, highlightbackground='gray1', fg='green')
    exit_button.pack(fill=Tk.X)

    # ball object
    bar = Bar()

    sys.stdout = Std_redirector(text)

    thread1 = threading.Thread(target=myfunc)
    thread1.start()

    root.mainloop()


# display(call_gen)
