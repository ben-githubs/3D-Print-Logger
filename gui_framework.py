# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:03:42 2020

@author: Ben
"""
###################################################################################################
# Imports                                                                                 Imports #
# -- System Modules -- #
from configparser import ConfigParser
from functools import partial
import logging
import os
from time import sleep
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import webbrowser


# -- Custom Modules -- #
import client
import server


###################################################################################################
# Global Parameters                                                             Global Paremeters #
CONFIG_FILE = r"client.ini"


###################################################################################################
# App Class                                                                             App Class #
""" This is the application window! """
class App(tk.Frame):
    # -- Class Attritbutes -- #
    app = None
    root = None
    title = "Logger"
    
    WIDTH = 720
    HEIGHT = 480
    
    # --------------------------------------------------------------------- App ----- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        if not App.app:
            App.app = self
            App.root = self.parent
        else:
            raise Exception("You cannot have more than one instance of 'App'.")
        
        
        self.logger = logging.getLogger("app.App")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        f = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
        ch.setFormatter(f)
        #if not len(self.logger.handlers):
            #self.logger.addHandler(ch)
        self.logger.debug("__init__: Logging initializd.")
        
        # LOAD CONF
        self.conf = ConfigParser()
        self.conf.read(CONFIG_FILE)
        self.localServer = self.conf.getboolean("LOGGER", "start local server")
        
        # Start Server and Client
        if self.localServer:
            self.server = server.Server("server.ini")
            self.logger.debug("__init__: Server started.")
        self.client = client.Client()
        self.logger.debug("__init__: Client started.")
        self.client.connect()
        self.logger.debug("__init__: Client connected.")
        
        
        self.configure(width=App.WIDTH, height=App.HEIGHT)
        self.bindHotkeys()
        self.addWidgets()
        
    
    # --------------------------------------------------------------------- App --- addWidgets () #
    def addWidgets(self):
        self.logger.debug("addWidgets: Adding widgets to main window.")
        self.menubar = tk.Menu(self)
        m = self.menubar
        
        m.add_command(label="Start", command=lambda: self.openFrame("Start"))
        
        printmenu = tk.Menu(m, tearoff=False)
        printmenu.add_command(label="New Print", command=lambda: self.openFrame("AddPrint"), accelerator="Ctrl+P")
        printmenu.add_command(label="Failed Print", command=lambda: self.openFrame("AddFailed"), accelerator="Ctrl+F")
        m.add_cascade(label="Prints", menu=printmenu)
        
        usermenu = tk.Menu(m, tearoff=False)
        usermenu.add_command(label="View Prints", command=lambda: self.openFrame("ListPrints"), accelerator="Ctrl+Shift+P")
        usermenu.add_command(label="Edit Rates", command=lambda: self.openFrame("ListRates"), accelerator="Ctrl+Shift+R")
        usermenu.add_command(label="Edit Printers", command=lambda: self.openFrame("ListPrinters"), accelerator="Ctrl+Shift+T")
        usermenu.add_command(label="Edit Users", command=lambda: self.openFrame("ListUsers"), accelerator="Ctrl+Shift+U")
        m.add_cascade(label="Edit", menu=usermenu)
        
        invoicemenu = tk.Menu(m, tearoff=False)
        invoicemenu.add_command(label="Create New Invoice", command=lambda: self.openFrame("AddInvoice"), accelerator="Ctrl+I")
        invoicemenu.add_command(label="View Invoices", command=lambda: self.openFrame("ListInvoices"), accelerator="Ctrl+Shift+I")
        invoicemenu.add_command(label="Log Payment", command=lambda: self.openFrame("LogPayment"), accelerator="Ctrl+M")
        invoicemenu.add_command(label="View Amounts Owing", command=lambda: self.openFrame("ViewOwing"), accelerator="Ctrl+Shift+M")
        m.add_cascade(label="Invoicing", menu=invoicemenu)
        
        m.add_command(label="Help", command=lambda: self.openHelp())
        
        self.parent.config(menu=m)
        self.logger.debug("addWidgets: Finished adding menu.")
        
        self.pack(fill="both", expand="true")
        
        self.frame = None    # This variable will hold a reference to the current frame in use
        self.frames = dict()    # This is a mapping of string names to each screen the app has
        
        self.columnconfigure(0, weight=1)
        
        self.logger.debug("addWidgets: Done.")
    
    
    # --------------------------------------------------------------------- App ------- addPage() #
    """ Adds a Page Class. """
    def addPage(self, tag, page):
        self.frames[tag] = page
    
    
    # --------------------------------------------------------------------- App ----- showFrame() #
    """ Switches the view to a different frame. """
    def showFrame(self, frame):
        self.logger.debug("showFrame: Switching frame to '{}'".format(frame))
        self.frames[frame].tkraise()
    
    
    # --------------------------------------------------------------------- App ----- openFrame() #
    """ Opens a new frame, makes it visible, and closes the previous frame. """
    def openFrame(self, frame, *args, **kwargs):
        self.logger.debug("openFrame: Opening new frame '{}'".format(frame))
        f = self.frames[frame](self, *args, **kwargs)
        if f.abort:
            return
        f.pack(fill="both", expand="true")
        if self.frame:
            self.frame.destroy()
        self.frame = f
    
    
    # --------------------------------------------------------------------- App -- bindHotkeys () #
    def bindHotkeys(self):
        self.parent.bind("<Control-p>", lambda e: self.openFrame("AddPrint"))
        self.parent.bind("<Control-P>", lambda e: self.openFrame("ListPrints"))
        self.parent.bind("<Control-f>", lambda e: self.openFrame("AddFailed"))
        self.parent.bind("<Control-u>", lambda e: self.openFrame("AddUser"))
        self.parent.bind("<Control-U>", lambda e: self.openFrame("ListUsers"))
        self.parent.bind("<Control-i>", lambda e: self.openFrame("AddInvoice"))
        self.parent.bind("<Control-I>", lambda e: self.openFrame("ListInvoices"))
        self.parent.bind("<Control-r>", lambda e: self.openFrame("AddRate"))
        self.parent.bind("<Control-R>", lambda e: self.openFrame("ListRates"))
        #self.parent.bind("<Control-t>", lambda e: self.openFrame("AddPrinter"))
        self.parent.bind("<Control-T>", lambda e: self.openFrame("ListPrinters"))
        self.parent.bind("<Control-m>", lambda e: self.openFrame("LogPayment"))
        self.parent.bind("<Control-M>", lambda e: self.openFrame("ViewOwing"))
    
    
    def openHelp(self):
        print("Opening Help")
        fname = os.path.abspath("docs//docs.html")
        webbrowser.open(fname, new=2)
    
    
    # --------------------------------------------------------------------- App ------- onExit () #
    """ Closes everything down. """
    def onExit(self):
        self.logger.info("Closing the program down.")
        self.logger.debug("onExit: Sending kill signal to server...")
        self.server._kill = True
        sleep(0.25)
        self.logger.debug("onExit: Closing client...")
        self.client.close()
        self.logger.debug("onExit: Client closed.")
        self.logger.debug("onExit: Closing main window.")
        self.parent.destroy()


###################################################################################################
# Page Class                                                                           Page Class #
class Page(tk.Frame):
    # -- Class Attributes -- #
    title = ""
    
    # -------------------------------------------------------------------- Page ----- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Ensure that there is an existing App object
        if not App.app:
            raise Exception("Cannot create a 'Page' instance without an existing 'App' instance.")
        
        # Load some useful handles
        self.client = App.app.client
        
        # Set up logging
        self.logger = logging.getLogger("app." + self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        f = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
        ch.setFormatter(f)
        if not len(self.logger.handlers):
            self.logger.addHandler(ch)
        
        # Update window title
        if self.__class__.title:
            App.root.title(App.title + " - " + self.__class__.title)
        else:
            App.root.title(App.title)
        
        
        # Make a flag to tell the program whether or not initialization was aborted
        self.abort = False
    
    
    # -------------------------------------------------------------------- Page --- addWidgets () #
    def addWidgets(self):
        pass


###################################################################################################
# UserVerify                                                                           UserVerify #
class UserVerify(tk.Toplevel):
    # Class Properties
    lastUserid = ""
    
    CANCELLED = 0
    BAD_LOGIN = 1
    WRONG_USER = 2
    GOOD_LOGIN = 3
    
    # -------------------------------------------------------------- UserVerify ------ __init__() # 
    def __init__(self, message, userid, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        
        self.entry1 = tk.StringVar()
        self.entry2 = tk.StringVar()
        self.userid = tk.StringVar()
        self.passwd = tk.StringVar()
        
        self.resizable(False, False)
        
        tk.Label(self, text=message).pack(fill="x", padx=5, pady=5)
        f = tk.Frame(self)
        tk.Label(f, text="User ID: ").grid(row=0, column=0, sticky="E")
        e = ttk.Entry(f, text=UserVerify.lastUserid, textvariable=self.entry1)
        e.grid(row=0, column=1, sticky="EW")
        e.focus()
        tk.Label(f, text="Password: ").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, show="•", textvariable=self.entry2).grid(row=1, column=1, sticky="EW")
        f.pack(fill="x", padx=5, pady=5)
        f.rowconfigure((0,1), pad=5)
        f.columnconfigure(0, weight=1, pad=5)
        f.columnconfigure(1, weight=2, pad=5)
        f = tk.Frame(self)
        ttk.Button(f, text="Submit", command=self.submit).grid(row=0, column=1, sticky="EW")
        ttk.Button(f, text="Cancel", command=self.cancel).grid(row=0, column=0, sticky="EW")
        f.pack(fill="x", padx=2, pady=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        
        self.bind("<Return>", lambda x: self.submit())
        self.bind("<Escape>", lambda x: self.cancel())
    
    
    # -------------------------------------------------------------- UserVerify -------- submit() #
    def submit(self):
        self.userid.set(self.entry1.get())
        self.passwd.set(self.entry2.get())
        UserVerify.lastUserid = self.userid.get()
        self.destroy()
    
    
    # -------------------------------------------------------------- UserVerify -------- cancel() #
    def cancel(self):
        self.destroy()
    
    
    # -------------------------------------------------------------- UserVerify ------ getLogin() #
    def getLogin(parent, message="Please enter your login information.", userid=lastUserid):
        win = UserVerify(message, userid)
        uservar = win.userid
        passvar = win.passwd
        win.grab_set()
        parent.wait_window(win)
        return (uservar.get(), passvar.get())
    
    
    # --------------------------------------------------
    def verifyLogin(parent, target="", message="Please enter your login information.", userid=lastUserid):
        win = UserVerify(message, userid)
        client = App.app.client
        uservar = win.userid
        passvar = win.passwd
        win.grab_set()
        parent.wait_window(win)
        
        userid, passwd = uservar.get(), passvar.get()
        
        if not userid and not passwd:
            return False, UserVerify.CANCELLED, userid, passwd
        if not client.user_verify(userid, passwd):
            return False, UserVerify.BAD_LOGIN, userid, passwd
        if target and not client.user_issuper(userid, passwd) and not userid == target:
            return False, UserVerify.WRONG_USER, userid, passwd
        
        return True, UserVerify.GOOD_LOGIN, userid, passwd
        


###################################################################################################
# EntryPopup                                                                           EntryPopup #
""" This class is an easy way to prompt the user for single-line text input via pop-up. """
class EntryPopup(tk.Toplevel):
    # -------------------------------------------------------------- EntryPopup ------ __init__() #
    def __init__(self, parent, title=None, message=None, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        
        row = 0
        if title:
            self.title = title
        if message:
            tk.Label(self, text=message).grid(row=row, column=0, columnspan=2, sticky="W")
            row += 1
        
        self.text = tk.StringVar()
        e = ttk.Entry(self, textvariable=self.text)
        e.grid(row=row, column=0, columnspan=2, sticky="EW")
        e.focus()
        row += 1
        
        ttk.Button(self, text="Submit", command=self.submit).grid(row=row, column=1, sticky="EW")
        ttk.Button(self, text="Cancel", command=self.cancel).grid(row=row, column=0, sticky="EW")
        
        self.columnconfigure((0,1), weight=1, pad=5)
        
        self.bind("<Return>", lambda x: self.submit())
        self.bind("<Escape>", lambda x: self.cancel())
    
    
    # -------------------------------------------------------------- EntryPopup -------- submit() #
    def submit(self):
        self.destroy()
    
    
    # -------------------------------------------------------------- EntryPopup -------- cancel() #
    def cancel(self):
        self.text.set("")
        self.destroy()
    
    
    # -------------------------------------------------------------- EntryPopup ------- getText() #
    def getText(root, title=None, message=None):
        top = EntryPopup(root, title=title, message=message)
        text = top.text
        top.grab_set()
        top.wait_window()
        return text.get()


###################################################################################################
# rn                                                                                           rn #
""" A nice class for keeping track of rownums in grid managers. """
class rn:
    # ---------------------------------------------------------------------- rn ----- __init__ () #
    def __init__(self, start=0):
        self.r = 0
    
    
    # ---------------------------------------------------------------------- rn ---------- row () #
    def row(self):
        return self.r
    
    
    # ---------------------------------------------------------------------- rn ---------- new () #
    def new(self):
        self.r += 1
        return self.r-1
    
    
    # ---------------------------------------------------------------------- rn -------- reset () #
    def reset(self, start=0):
        self.r = start


###################################################################################################
# CheckMenu                                                                             CheckMenu #
class CheckMenu(ttk.Menubutton):
    """ CheckMenu provides a dropdown list, which the user can click to select various options.
    options is a list of options to display. """
    def __init__(self, *args, **kwargs):
        options = []
        if "options" in kwargs:
            options = kwargs.pop("options")
        
        ttk.Menubutton.__init__(self, *args, **kwargs)
        self.menu = tk.Menu(self, tearoff=False)
        self.configure(menu=self.menu)
        
        self.options = dict()
        assert type(options) == list, "'options' must be a list."
        for opt in options:
            assert type(opt) == str, "Expected <str>, got <{}>".format(type(opt))
            self.options[opt] = tk.IntVar(value=0)
            self.menu.add_checkbutton(label=opt, variable=self.options[opt], onvalue=1, offvalue=0,
                                      command=self.cb)
        
    def cb(self):
        self.event_generate("<<Invoke>>")
    
    
    def getOptions(self):
        return [key for key in self.options.keys() if self.options[key].get() == 1]


###################################################################################################
# TableView                                                                             TableView #
class TableView(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        # Default arguments
        if "columns" not in kwargs:
            kwargs["columns"] = ()
        if "show" not in kwargs:
            kwargs["show"] = "headings"
        
        ttk.Treeview.__init__(self, *args, **kwargs)
        self.sortcol = 0   # This is the column from which to use the values for sorting
        self._rows = list()
        self.columns = kwargs["columns"]
        
        i = 0
        for col in self.columns:
            i += 1
            self.heading(col, text=col, command=partial(self.sort, i))
    
    
    """ Adds a new row to the table.
    Args  -  tup: a tuple containing (ITEM, VAL1, VAL2, ...), where ITEM is the actual object or
                  value the row represents, and VAL1, ..., VALN are the values to display in the
                  columns of the table.
    """
    def addRow(self, tup):
        assert len(tup) == len(self.columns)+1, "Row does not have the proper number of values for each column."
        self._rows.append(tup)
        self.refresh()
    
    
    def sort(self, col):
        assert type(col) == int, "'col' must be an integer."
        assert 0 <= col <= len(self.columns)+1, "'col' is out of range."
        self.sortcol = col
        self.refresh()
    
    
    def refresh(self):
        # Rearrange the rows
        if self.sortcol != 0:
            _rows = sorted(self._rows, key=lambda tup: tup[self.sortcol])
            if self._rows == _rows:
                self._rows = _rows[::-1]
            else:
                self._rows = _rows
        # Delete existing items in tree
        self.delete(*self.get_children())
        # Add new entries in proper order
        for tup in self._rows:
            self.insert("", "end", values=tup[1:])
    
    
    """ Removes all entries in the table. """
    def empty(self):
        self._rows = list()
        self.refresh()
    
    
    """ Returns a list of the selected rows. """
    def getRows(self):
        return [self._rows[self.index(sel)] for sel in self.selection()]
    
    
    def getIndex(self):
        return [self.index(sel) for sel in self.selection()]