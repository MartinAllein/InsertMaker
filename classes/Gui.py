from tkinter import *


class Gui:

    def __init__(self):
        self.root = Tk()

    def init(self):
        mylabel = Label(self.root, text="Hello world")
        mylabel.pack();

        self.root.mainloop();
