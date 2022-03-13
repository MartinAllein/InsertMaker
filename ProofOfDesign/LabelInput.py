from datetime import datetime
import os
import csv
import tkinter as tk
from tkinter import ttk


class LabelInput(tk.Frame):
    """A widget containing a label and input together."""

    def __init__(self, parent, label='', input_class=ttk.Entry,
                 input_var=None, input_args=None, label_args=None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = input_var
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = input_var

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        if self.variable:
            return self.variable.get()
        elif type(self.input) == tk.Text:
            return self.input.get('1.0', tk.END)
        else:
            return self.input.get()

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input).__name__.endswith('button'):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value)
