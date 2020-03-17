# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 14:18:09 2020

@author: Ben
"""
###################################################################################################
# Imports                                                                                 Imports #
import logging
import tkinter as tk
from tkinter import ttk

from gui_framework import App, Page
import gui_prints, gui_users, gui_misc, gui_invoices

###################################################################################################
# Global Setup                                                                       Global Setup #
form = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
ch.setFormatter(form)
fh = logging.FileHandler("makerspace.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(form)
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.addHandler(ch)
logger.addHandler(fh)


###################################################################################################
# StartPage                                                                             StartPage #
class StartPage(Page):
    title = "Start"
    
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        self.addWidgets()
    
    def addWidgets(self):
        f = tk.Frame(self)
        tk.Label(f, text="Quickstart").grid(row=0, column=0, sticky="N")
        ttk.Button(f, text="Add New Print", command=lambda: App.app.openFrame("AddPrint")).grid(row=1, column=0, sticky="EW")
        ttk.Button(f, text="Add Failed Print", command=lambda: App.app.openFrame("AddFailed")).grid(row=2, column=0, sticky="EW")
        ttk.Button(f, text="Add New User", command=lambda: self.parent.openFrame("AddUser")).grid(row=3, column=0, sticky="EW")
        f.columnconfigure(0, minsize=160)
        f.rowconfigure((0,1,2,3), pad=2)
        f.pack(side="top")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    # Add Frames
    app.addPage("Start", StartPage)
    
    app.addPage("ListUsers", gui_users.ListUserPage)
    app.addPage("AddUser", gui_users.AddUserPage)
    app.addPage("EditUser", gui_users.EditUserPage)
    app.addPage("ListPrints", gui_prints.ListPrintsPage)
    app.addPage("AddPrint", gui_prints.AddPrintPage)
    app.addPage("EditPrint", gui_prints.EditPrintPage)
    app.addPage("AddFailed", gui_prints.AddFailedPage)
    app.addPage("ListRates", gui_misc.ListRatePage)
    app.addPage("AddRate", gui_misc.AddRatePage)
    app.addPage("ListPrinters", gui_misc.ListPrinterPage)
    app.addPage("ListInvoices", gui_invoices.ListInvoicePage)
    app.addPage("AddInvoice", gui_invoices.AddInvoicePage)
    app.addPage("LogPayment", gui_invoices.LogPaymentPage)
    app.addPage("ViewOwing", gui_invoices.ViewOwingPage)
    app.openFrame("Start")
    
    
    root.geometry('{}x{}'.format(App.WIDTH, App.HEIGHT))
    root.wm_iconbitmap('logo.ico')
    root.protocol("WM_DELETE_WINDOW", app.onExit)
    root.mainloop()
    