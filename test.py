# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:42:57 2020

@author: Ben
"""

import tkinter as tk

def validate(s):
    print("Validating...")
    return False


root = tk.Tk()
root.register(validate)
tk.Entry(root, validate="key", validatecommand=(validate, "%P")).pack()

root.mainloop()