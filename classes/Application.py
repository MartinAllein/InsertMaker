import tkinter as tk
from tkinter import ttk

# Label    Label
# Entry    Texteingabe  width=xx, borderwidth=
PROGRAM_NAME = ' Explosion Drum Machine '


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Hello Tkinter")
        self.geometry("800x600")
        self.resizable(width=False, height=False)
