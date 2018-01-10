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
from all_colors import COLORS, GRAY_COLORS, TRANSITION_COLORS
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
    while not exit_success:
        time.sleep(.5)  # wait for exit success
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

DEFAULT_BAR_SPEED = 10
SLEEPING_BAR_COLOR = "SpringGreen4"
SLEEPING_BAR_SPEED = 2
LOADING_BAR_SPEED = 40
LOADING_BAR_COLOR = "green"
BAR_MODE = "listening"  # other options, listening, sleeping, grabbing shifts
ALL_GREENS = [s for s in COLORS if 'green' in s]


class Bar:
    def __init__(self):
        self.shape = canvas.create_rectangle(0, 0, SIZE, SIZE, fill=color)
        self.speedx = DEFAULT_BAR_SPEED  # changed from 3 to 9
        self.speedy = 0  # changed from 3 to 9
        self.active = True
        self.move_active()

    def bar_update(self):
        canvas.move(self.shape, self.speedx, self.speedy)
        pos = canvas.coords(self.shape)
        if BAR_MODE == "listening":
            global DEFAULT_BAR_SPEED
            self.speedx = DEFAULT_BAR_SPEED
            if pos[2] - OFFSET >= WIDTH or pos[0] <= - OFFSET:
                self.speedx *= -1
                DEFAULT_BAR_SPEED = self.speedx
            if pos[3] >= HEIGHT or pos[1] <= 0:
                self.speedy *= -1
        elif BAR_MODE == "loading":
            self.speedx = LOADING_BAR_SPEED
            if pos[0] >= OFFSET:
                canvas.coords(self.shape, -500, 0, 0, 500)
                canvas.itemconfig(self.shape, fill=LOADING_BAR_COLOR)
        elif BAR_MODE == "sleeping":
            canvas.coords(self.shape, 0, 0, 500, 500)
            canvas.itemconfig(self.shape, fill=SLEEPING_BAR_COLOR)

    def move_active(self):
        if self.active:
            self.bar_update()
            root.after(15, self.move_active)  # changed from 10ms to 30ms


################################################################################
#

# function to simulate color fading
# for sleep mode
def gray_fade_in():
    for gray in GRAY_COLORS:
        global SLEEPING_BAR_COLOR
        SLEEPING_BAR_COLOR = gray
        time.sleep(.01)


# function to simulate color fading out
# for sleep mode
def gray_fade_out():
    for gray in list(reversed(GRAY_COLORS)):
        global SLEEPING_BAR_COLOR
        SLEEPING_BAR_COLOR = gray
        time.sleep(.01)


# function to transition through different colors
# for wiating to grab shifts
def colors_transition():
    for color in TRANSITION_COLORS:
        global LOADING_BAR_COLOR
        LOADING_BAR_COLOR = color
        time.sleep(.05)


def display(myfunc):
    exit_button = Tk.Button(root, text='Exit', command=stop_thread, pady=0, padx=0, highlightbackground='gray1', fg='green')
    exit_button.pack(fill=Tk.X)

    # ball object
    bar = Bar()
    # change color

    sys.stdout = Std_redirector(text)

    thread1 = threading.Thread(target=myfunc)
    thread1.start()

    root.mainloop()


# display(call_gen)
