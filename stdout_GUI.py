###############################################################################
"""
Program description

Created by:	skeleton by Billy Koech
Date:		Jan 4th 2018

mru(most recent update):

"""
###############################################################################
# import modules
import sys  # module to access output
# from Tkinter import *  # GUI module
import Tkinter

# program variables

# user variables

###############################################################################
# program functions
###############################################################################



################################################################################
#############Incomplete module based on functions found on the internet#########
################    I do not claim this to be my work   ########################
################################################################################
"""
root = Tk()  # open GUI
root.title('Shiftboard Handler')  # title
root.geometry("345x230")		# dimension of GUI
S = Scrollbar(root)
S.pack(side=RIGHT, fill=Y)
window = Text(root)
window.pack()


# clas to print to window
class PrintToWindow(object):
    def write(self, s):
        window.insert(END, s)


sys.stdout = PrintToWindow()
print 'Hello, world!'
print "Isn't this fun!"
"""

"""
class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        toolbar = tk.Frame(self)
        toolbar.pack(side="top", fill="x")
        b1 = tk.Button(self, text="print to stdout", command=self.print_stdout)
        b2 = tk.Button(self, text="print to stderr", command=self.print_stderr)
        b1.pack(in_=toolbar, side="left")
        b2.pack(in_=toolbar, side="left")
        self.text = tk.Text(self, wrap="word")
        self.text.pack(side="top", fill="both", expand=True)
        self.text.tag_configure("stderr", foreground="#b22222")


        sys.stdout = TextRedirector(self.text, "stdout")
        sys.stderr = TextRedirector(self.text, "stderr")

    def print_stdout(self):
        '''Illustrate that using 'print' writes to stdout'''
        print "this is stdout"

    def print_stderr(self):
        '''Illustrate that we can write directly to stderr'''
        sys.stderr.write("this is stderr\n")


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")


app = ExampleApp()
print('everything')
app.mainloop()

"""
''' Demonstrate python interpreter output in Tkinter Text widget

type python expression in the entry, hit DoIt and see the results
in the text pane.'''

'''
class Display(Frame):
    def __init__(self, parent=0):
        Frame.__init__(self, parent)
        self.entry = Entry(self)
        self.entry.pack()
        self.doIt = Button(self, text="DoIt", command=self.onEnter)
        self.doIt.pack()
        self.output = Text(self)
        self.output.pack()
        sys.stdout = self
        self.pack()

    def onEnter(self):
        print eval(self.entry.get())

    def write(self, txt):
        self.output.insert(END, str(txt))

    print("this is a test")


if __name__ == '__main__':
    Display().mainloop()
'''


class CoreGUI(object):
    def __init__(self, parent):
        text_box = Tkinter.Text(parent, state=Tkinter.DISABLED)
        text_box.pack()

        output_button = Tkinter.Button(parent, text="Output", command=self.main)
        output_button.pack()

    def main(self):
        print "Std Output"
        raise ValueError("Std Error")


root = Tkinter.Tk()
CoreGUI(root)
root.mainloop()


class StdRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.config(state=Tkinter.NORMAL)
        self.text_space.insert("end", string)
        self.text_space.see("end")
        self.text_space.config(state=Tkinter.DISABLED)


sys.stdout = StdRedirector(root.text_box)
sys.stderr = StdRedirector(root.text_box)
# Main entry point for the script.


def main():
    print("This is a test")


if __name__ == '__main__':
    main()
