# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 14:18:09 2020

@author: Ben
"""
###################################################################################################
# Imports                                                                                 Imports #
import logging
from datetime import datetime
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox

import natsort

from benutil import struct, isfloat, isint
import client, server

###################################################################################################
# Global Setup                                                                       Global Setup #
format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(format)
if not len(logger.handlers):
    logger.addHandler(ch)

WIDTH = 720
HEIGHT = 480

IMAGE_PATH = "main_bg.png"


###################################################################################################
# App Class                                                                             App Class #
""" This is the application window! """
class App(tk.Frame):
    # --------------------------------------------------------------------- App ----- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.logger = logging.getLogger("app.App")
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(format)
        if not len(self.logger.handlers):
            self.logger.addHandler(ch)
        self.logger.debug("__init__: Logging initializd.")
        
        self.server = server.Server("server.ini")
        self.logger.debug("__init__: Server started.")
        self.client = client.Client()
        self.logger.debug("__init__: Client started.")
        self.client.connect()
        self.logger.debug("__init__: Client connected.")
        
        
        self.configure(width=WIDTH, height=HEIGHT)
        self.addWidgets()
        
    
    # --------------------------------------------------------------------- App --- addWidgets () #
    def addWidgets(self):
        self.logger.debug("addWidgets: Adding widgets to main window.")
        self.menubar = tk.Menu(self)
        m = self.menubar
        
        printmenu = tk.Menu(m, tearoff=False)
        printmenu.add_command(label="New Print", command=lambda: self.openFrame("AddPrint"))
        printmenu.add_command(label="Failed Print", command=lambda: self.openFrame("AddFailed"))
        m.add_cascade(label="Prints", menu=printmenu)
        
        usermenu = tk.Menu(m, tearoff=False)
        usermenu.add_command(label="View Prints", command=lambda: self.openFrame("ListPrints"))
        usermenu.add_command(label="Edit Rates", command=lambda: self.openFrame("ListRates"))
        usermenu.add_command(label="Edit Printers", command=lambda: self.openFrame("ListPrinters"))
        usermenu.add_command(label="Edit Users", command=lambda: self.openFrame("ListUsers"))
        m.add_cascade(label="Edit", menu=usermenu)
        
        invoicemenu = tk.Menu(m, tearoff=False)
        invoicemenu.add_command(label="Create New Invoice")
        invoicemenu.add_command(label="View Invoices")
        invoicemenu.add_command(label="View Amounts Owing")
        m.add_cascade(label="Invoicing", menu=invoicemenu)
        
        self.parent.config(menu=m)
        self.logger.debug("addWidgets: Finished adding menu.")
        
        
        self.pack(fill="both")
        
        self.frame = None    # This variable will hold a reference to the current frame in use
        self.frames = dict()    # This is a mapping of string names to each screen the app has
        self.frames["Start"] = StartPage
        
        self.frames["AddUser"] = AddUserPage
        self.frames["ListUsers"] = ListUserPage
        self.frames["EditUser"] = EditUserPage
        
        self.frames["AddPrint"] = AddPrintPage
        self.frames["ListPrints"] = ListPrintsPage
        self.frames["AddFailed"] = AddFailedPage
        
        self.frames["AddRate"] = AddRatePage
        self.frames["ListRates"] = ListRatePage
        
        self.frames["ListPrinters"] = ListPrinterPage
        
        self.columnconfigure(0, weight=1)
        
        self.openFrame("Start")
        self.logger.debug("addWidgets: Finished adding frames.")
        self.logger.debug("addWidgets: Done.")
    
    
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
        f.grid(row=0, column=0, sticky="news")
        if self.frame:
            self.frame.destroy()
        self.frame = f
    
    
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
# StartPage                                                                             StartPage #
class StartPage(tk.Frame):
    # --------------------------------------------------------------- StartPage ----- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.logger = logging.getLogger("app.StartPage")
        
        self.addWidgets()
    
    def addWidgets(self):
        tk.Label(self, text="Welcome!").pack(fill="both")


###################################################################################################
# AddUserPage                                                                         AddUserPage #
class AddUserPage(tk.Frame):
    # ----------------------------------------------------------- AddUserPage ------- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        logger = logging.getLogger("app.AddUserPage")
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(format)
        if not len(logger.handlers):
            logger.addHandler(ch)
        self.logger = logger
        
        self.addWidgets()
    
    
    # ----------------------------------------------------------- AddUserPage ----- addWidgets () #
    def addWidgets(self):
        s = struct()
        self.vars = s
        s.userid = tk.StringVar()
        s.passwd1 = tk.StringVar()
        s.passwd2 = tk.StringVar()
        s.issuper = tk.BooleanVar()
        s.email = tk.StringVar()
        s.firstname = tk.StringVar()
        s.lastname = tk.StringVar()
        s.auth_userid = tk.StringVar()
        s.auth_passwd = tk.StringVar()
        
        # Basic Info Frame
        f = ttk.Labelframe(self, text="Login Information")
        tk.Label(f, text="User ID:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvariable=s.userid).grid(row=0, column=1, sticky="W")
        tk.Label(f, text="Password:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, show="•", textvariable=s.passwd1).grid(row=1, column=1, sticky="W")
        tk.Label(f, text="Repeat Password:").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, show="•", textvariable=s.passwd2).grid(row=2, column=1, sticky="W")
        ttk.Checkbutton(f, text="Give evelated privaleges?", var=s.issuper).grid(row=3, column=1, sticky="W")
        
        f.rowconfigure((0,1,2,3), pad=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        f.pack(fill="x", padx=10, pady=10)
        
        # Authotization Frame
        f = ttk.Labelframe(self, text="Authorization")
        tk.Label(f, text="Please have a moderator fill this section.").grid(row=0, column=0, columnspan=2)
        tk.Label(f, text="Mod User ID:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, textvar=s.auth_userid).grid(row=1, column=1, sticky="W")
        tk.Label(f, text="Mod Password:").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, show="•", textvar=s.auth_passwd).grid(row=2, column=1, sticky="W")
        
        f.rowconfigure((0,1,2,3), pad=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        f.pack(fill="x", padx=10, pady=10)
        
        # Auxillary Info Frame
        f = ttk.LabelFrame(self, text="Other Information")
        tk.Label(f, text="Student/Staff Email:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvar=s.email, width=40).grid(row=0, column=1, sticky="W")
        tk.Label(f, text="First Name:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, textvar=s.firstname).grid(row=1, column=1, sticky="W")
        tk.Label(f, text="Last/Organization Name:").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, textvar=s.lastname).grid(row=2, column=1, sticky="W")
        
        f.rowconfigure((0,1,2,3), pad=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        f.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(self, text="Create User", command=self.addUser).pack()
    
    
    # ----------------------------------------------------------- AddUserPage ---- verifyInput () #
    def verifyInput(self):
        if self.vars.userid.get() == "" or self.vars.passwd1.get() == "" or self.vars.passwd2.get() == "":
            self.logger.debug("verifyInput: User ID and/or password entries are blank.")
            return False
        elif self.vars.issuper.get():
            if self.vars.auth_userid.get() == "" or self.vars.auth_passwd.get() == "":
                self.logger.debug("verifyInput: Proposed user is privaledged, but no authorization information is supplied.")
                return False
        
        if self.vars.passwd1.get() != self.vars.passwd2.get():
            self.logger.debug("verifyInput: Passwords do not match.")
            return False
        else:
            return True
    
    
    # ----------------------------------------------------------- AddUserPage ----- clearInput () #
    def clearInput(self):
        s = self.vars
        s.userid.set("")
        s.passwd1.set("")
        s.passwd2.set("")
        s.issuper.set(False)
        s.email.set("")
        s.firstname.set("")
        s.lastname.set("")
        s.auth_userid.set("")
        s.auth_passwd.set("")
    
    
    # ----------------------------------------------------------- AddUserPage -------- addUser () #
    def addUser(self):
        client = self.parent.client
        
        uid = self.vars.userid.get()
        pwd = self.vars.passwd1.get()
        sup = bool(self.vars.issuper.get())
        eml = self.vars.email.get()
        fnm = self.vars.firstname.get()
        lnm = self.vars.lastname.get()
        auid = self.vars.auth_userid.get()
        apwd = self.vars.auth_passwd.get()
        
        if self.verifyInput():
            try:
                if not sup:
                    client.user_add(uid, pwd, email=eml, firstname=fnm, lastname=lnm)
                else:
                    client.add_user(uid, pwd, issuper=sup, auth_userid=auid, auth_passwd=apwd, 
                                   email=eml, firstname=fnm, lastname=lnm)
                messagebox.showinfo("Info", "New user successfully created!")
                self.clearInput()
            except Exception as e:
                logger.exception("An error occured while verifying input.")
                messagebox.showerror("Error", "Something went wrong while adding the new user:\n\n{}".format(str(e)))
        else:
            messagebox.showinfo("Missing Information", "Please fill out the required fields.")


###################################################################################################
# EditUserPage                                                                       EditUserPage #
class EditUserPage(AddUserPage):
    # ------------------------------------------------------------ EditUserPage ----- __init__ () #
    def __init__(self, parent, userid, elevated=False, auth=("",""), *args, **kwargs):
        AddUserPage.__init__(self, parent, *args, **kwargs)
        self.userid = userid
        self.elevated = elevated
        self.auth = auth # Holds the info of whoever is authorizing the changes
        
        self.loadUser(userid, elevated=elevated)
    
    
    # ------------------------------------------------------------ EditUserPage ------ loadUser() #
    def loadUser(self, userid, elevated=False):
        u = self.parent.client.user_get(userid)[0]
        self.vars.userid.set(u.userid)
        self.vars.issuper.set(u.issuper)
        self.vars.email.set(u.email)
        self.vars.firstname.set(u.firstname)
        self.vars.lastname.set(u.lastname)
        
        if elevated:
            self.check.configure(state=tk.NORMAL)
        else:
            self.check.configure(state=tk.DISABLED)
    
    
    # ------------------------------------------------------------ EditUserPage ---- addWidgets() #
    def addWidgets(self):
        s = struct()
        self.vars = s
        s.userid = tk.StringVar()
        s.passwd1 = tk.StringVar()
        s.passwd2 = tk.StringVar()
        s.issuper = tk.BooleanVar()
        s.email = tk.StringVar()
        s.firstname = tk.StringVar()
        s.lastname = tk.StringVar()
        
        # Basic Info Frame
        f = ttk.Labelframe(self, text="Login Information")
        tk.Label(f, text="User ID:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvariable=s.userid, state=tk.DISABLED).grid(row=0, column=1, sticky="W")
        tk.Label(f, text="Password:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, show="•", textvariable=s.passwd1).grid(row=1, column=1, sticky="W")
        tk.Label(f, text="Repeat Password:").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, show="•", textvariable=s.passwd2).grid(row=2, column=1, sticky="W")
        self.check = ttk.Checkbutton(f, text="Give evelated privaleges?", var=s.issuper, state=tk.DISABLED)
        self.check.grid(row=3, column=1, sticky="W")
        
        f.rowconfigure((0,1,2,3), pad=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        f.pack(fill="x", padx=10, pady=10)
        
        # Auxillary Info Frame
        f = ttk.LabelFrame(self, text="Other Information")
        tk.Label(f, text="Student/Staff Email:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvar=s.email, width=40).grid(row=0, column=1, sticky="W")
        tk.Label(f, text="First Name:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, textvar=s.firstname).grid(row=1, column=1, sticky="W")
        tk.Label(f, text="Last/Organization Name:").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, textvar=s.lastname).grid(row=2, column=1, sticky="W")
        
        f.rowconfigure((0,1,2,3), pad=2)
        f.columnconfigure((0,1), weight=1, pad=5)
        f.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(self, text="Save Changes", command=self.save).pack()
    
    
    # ------------------------------------------------------------ EditUserPage ---------- save() #
    def save(self):
        # Verify everything
        if self.vars.passwd1.get() or self.vars.passw2.get():
            if self.vars.passwd1.get() != self.vars.passwd2.get():
                messagebox.error("Invalid", "Passwords do not match.")
        
        # Copy everything
        v = self.vars
        try:
            self.parent.client.user_edit(v.userid.get(), self.auth[0], self.auth[1], 
                                        issuper=v.issuper.get(), email=v.email.get(), passwd=v.passwd1.get(),
                                        firstname=v.firstname.get(), lastname=v.lastname.get())
            messagebox.showinfo("Saved", "Changes successfully saved!")
        except Exception as e:
            logger.exception("EditUserPage.save")
            messagebox.showerror("Error", str(e))


###################################################################################################
# ListPrintsPage                                                                   ListPrintsPage #
class ListPrintsPage(tk.Frame):
    # ---------------------------------------------------------- ListPrintsPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        
        self.prints = self.client.print_get()
        self.rates = natsort.natsorted(self.client.rate_get(), key=lambda x: x.name)
        
        self.addWidgets()
        self.refreshTree(self.prints)
    
    # ---------------------------------------------------------- ListPrintsPage ---- addWidgets() #
    def addWidgets(self):
        self.vars = struct()
        v = self.vars
        v.f_printid = tk.StringVar()
        v.f_rate = tk.StringVar(value="All")
        v.f_useridPrint = tk.StringVar()
        v.f_useridPay = tk.StringVar()
        v.f_lengthMin = tk.DoubleVar(value=0.0)
        v.f_lengthMax = tk.DoubleVar(value=999.0)
        v.f_durationMin = tk.IntVar(value=0)
        v.f_durationMax = tk.IntVar(value=999)
        v.f_dateMin = tk.StringVar()
        v.f_dateMax = tk.StringVar()
        v.f_finished = tk.StringVar(value="Both")
        
        self.rateDict = dict()
        for r in self.rates:
            self.rateDict[r.name] = r
        
        
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="Open Print", width=20, command=self.edit).pack(side="top")
        ttk.Button(f, text="Delete Print", width=20, command=self.delete).pack(side="top")
        ttk.Button(f, text="Filter", width=20, command=self.filt).pack(side="bottom")
        f.pack(side="right", fill="y")
        
        # Add List
        columns = ("printid", "userid", "date",)
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.column("printid", width=100, anchor="w")
        self.tree.heading("printid", text="Print ID", command=lambda: self.sort(0))
        self.tree.column("userid", width=100, anchor="w")
        self.tree.heading("userid", text="User ID", command=lambda: self.sort(1))
        self.tree.column("date", width=100, anchor="w")
        self.tree.heading("date", text="Date Logged", command=lambda: self.sort(2))
        self.tree.pack(fill="both")
        
        f = tk.Frame(self)
        f.columnconfigure((0,1,2,3), weight=1, pad=5)
        f.rowconfigure((0,1,2), weight=1, pad=5)
        tk.Label(f, text="Print ID").grid(row=0, column=0, sticky="W")
        tk.Label(f, text="User ID (printer)").grid(row=1, column=0, sticky="W")
        tk.Label(f, text="User ID (payer)").grid(row=2, column=0, sticky="W")
        ttk.Entry(f, textvar=v.f_printid).grid(row=0, column=1, sticky="EW")
        ttk.Entry(f, textvar=v.f_useridPrint).grid(row=1, column=1, sticky="EW")
        ttk.Entry(f, textvar=v.f_useridPay).grid(row=2, column=1, sticky="EW")
        
        tk.Label(f, text="Length (Min/Max)").grid(row=0, column=2, sticky="W")
        tk.Label(f, text="Duration (Min/Max)").grid(row=1, column=2, sticky="W")
        tk.Label(f, text="Date (Min/Max)").grid(row=2, column=2, sticky="W")
        ff = tk.Frame(f)
        ttk.Entry(ff, textvar=v.f_lengthMin, width=10).pack(side="left", fill="x")
        ttk.Entry(ff, textvar=v.f_lengthMax, width=10).pack(side="right", fill="x")
        ff.grid(row=0, column=3, sticky="EW")
        ff = tk.Frame(f)
        ttk.Entry(ff, textvar=v.f_durationMin, width=10).pack(side="left", fill="x")
        ttk.Entry(ff, textvar=v.f_durationMax, width=10).pack(side="right", fill="x")
        ff.grid(row=1, column=3, sticky="EW")
        ff = tk.Frame(f)
        ttk.Entry(ff, textvar=v.f_dateMin, width=10).pack(side="left", fill="x")
        ttk.Entry(ff, textvar=v.f_dateMax, width=10).pack(side="right", fill="x")
        ff.grid(row=2, column=3, sticky="EW")
        f.pack(side="bottom", fill="x")
        
        rateOpts = ["All"] + [r.name for r in self.rates]
        finOpts = ["All", "Yes", "No"]
        tk.Label(f, text="Rate").grid(row=3, column=0, sticky="W")
        tk.Label(f, text="Finished?").grid(row=3, column=2, sticky="W")
        ttk.Combobox(f, textvar=v.f_rate, values=rateOpts, state="readonly").grid(row=3, column=1, sticky="EW")
        ttk.Combobox(f, textvar=v.f_finished, values=finOpts, state="readonly").grid(row=3, column=3, sticky="EW")
        
        self.grid(row=0, column=0, sticky="NEWS")
    
    
    # ---------------------------------------------------------- ListPrintsPage --- refreshTree() #
    def refreshTree(self, prints):
        # Get list of users
        self.tree.delete(*self.tree.get_children())
        for p in prints:
            vals = (p.printid, p.userid, p.date.isoformat())
            self.tree.insert("", 0, text="", values=vals)
    
    
    # ---------------------------------------------------------- ListPrintsPage -------- verify() #
    def verify(self):
        msgBase = "The following errors were found while parsing your filter criteria:\n\n"
        msg = msgBase
        v = self.vars
        
        if not isfloat(v.f_lengthMin.get()) or float(v.f_lengthMin.get()) < 0:
            msg += "Min. length must be a number greater than 0.\n"
        if not isfloat(v.f_lengthMax.get()) or float(v.f_lengthMax.get()) < 0:
            msg += "Max. length must be a number greater than 0.\n"
        if not isint(v.f_durationMin.get()) or int(v.f_durationMin.get()) < 0:
            msg += "Min. duration must be an integer greater than 0.\n"
        if not isint(v.f_durationMax.get()) or int(v.f_durationMax.get()) < 0:
            msg += "Max. duration must be an integer greater than 0.\n"
        if v.f_dateMin.get():
            try:
                datetime.fromisoformat(v.f_dateMin.get())
            except ValueError:
                msg += "Min. date must be formatted as 'YYYY-MM-DD'.\n"
        if v.f_dateMax.get():
            try:
                datetime.fromisoformat(v.f_dateMax.get())
            except ValueError:
                msg += "Max. date must be formatted as 'YYYY-MM-DD'.\n"
        
        if msg != msgBase:
            messagebox.showerror("Bad Input", msg)
            return False
        else:
            return True
    
    
    # ---------------------------------------------------------- ListPrintsPage ---------- filt() #
    def filt(self):
        # First, check input, and quit if it's not valid
        valid = self.verify()
        if not valid:
            return
        
        # Then, parse filter criteria
        kwargs = dict()
        v = self.vars
        if v.f_printid.get():
            kwargs["printid"] = v.f_printid.get()
        if v.f_useridPrint.get():
            kwargs["userid"] = v.f_useridPrint.get()
        if v.f_useridPay.get():
            kwargs["paidby"] = v.f_useridPay.get()
        if v.f_rate.get() != "All":
            kwargs["rate"] = self.rateDict[v.f_rate.get()]
        
        if v.f_lengthMin.get():
            kwargs["lengthMin"] = float(v.f_lengthMin.get())
        if v.f_lengthMax.get():
            kwargs["lengthMax"] = float(v.f_lengthMax.get())
        
        if v.f_durationMin.get():
            kwargs["durationMin"] = int(v.f_durationMin.get())
        if v.f_durationMax.get():
            kwargs["durationMax"] = int(v.f_durationMax.get())
        
        if v.f_dateMin.get():
            kwargs["dateMin"] = datetime.fromisoformat(v.f_dateMin.get())
        if v.f_dateMax.get():
            kwargs["dateMax"] = datetime.fromisoformat(v.f_dateMax.get())
        
        if v.f_finished.get() != "Both":
            kwargs["finished"] = v.f_finished.get() == "Yes"
        
        # Next, get list of filtered print jobs
        filteredPrints = self.client.print_get(**kwargs)
        
        # Update the treeview
        self.refreshTree(filteredPrints)
    
    
    # ---------------------------------------------------------- ListPrintsPage ---------- edit() #
    def edit(self, *args, **kwargs):
        pass
    
    
    # ---------------------------------------------------------- ListPrintsPage -------- delete() #
    def delete(self, *args, **kwargs):
        pass


###################################################################################################
# AddPrintPage                                                                       AddPrintPage #
class AddPrintPage(tk.Frame):
    # ------------------------------------------------------------ AddPrintPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        
        self.rates = self.client.rate_get()
        self.printers = self.client.printer_get()
        
        self.addWidgets()
        self.enablePayerEntry()
    
    
    # ------------------------------------------------------------ AddPrintPage ---- addWidgets() #
    def addWidgets(self):
        self.vars = struct()
        v = self.vars
        v.userid = tk.StringVar()
        v.passwd = tk.StringVar()
        v.isPayer = tk.IntVar()
        v.payer = tk.StringVar()
        v.length = tk.StringVar()
        v.durationHr = tk.StringVar()
        v.durationMin = tk.StringVar()
        v.rate = tk.StringVar()
        v.printer = tk.StringVar()
        
        # -- Entry Validation -----
        # In the entries in the form, we add validation commands to prevent people from typing in
        # wrong values (like putting letters in a length entry, for example). We register each
        # function we'll use to check, and then we assign them to the specific entries as we create
        # them.
        
        rownum = rn()
        r = rownum.row
        n = rownum.new
        
        content = tk.Frame(self, width=500)
        
        # User and Billing Info
        f = ttk.Labelframe(content, text="User Info", width=500)
        tk.Label(f, text="User ID").grid(row=r(), column=0, sticky="E")
        ttk.Entry(f, textvar=v.userid).grid(row=n(), column=1, sticky="EW")
        
        tk.Label(f, text="Password").grid(row=r(), column=0, sticky="E")
        ttk.Entry(f, show="•", textvar=v.passwd).grid(row=n(), column=1, sticky="EW")
        
        ttk.Checkbutton(f, text="Is a different user paying for this print?", 
                        variable=v.isPayer, command=self.enablePayerEntry).grid(row=n(), column=0,
                                                                               columnspan=2)
        tk.Label(f, text="User ID").grid(row=r(), column=0, sticky="E")
        self.payeeEntry = ttk.Entry(f, textvar=v.payer)
        self.payeeEntry.grid(row=n(), column=1, sticky="EW")
        
        f.rowconfigure([i for i in range(f.grid_size()[1])], pad=2)
        f.columnconfigure([0,1], weight=1, pad=5)
        f.grid(row=0, column=0, sticky="EW")
        
        # Print Info
        f = ttk.Labelframe(content, text="Print Info")
        rownum.reset()
        
        tk.Label(f, text="Length of print (m):").grid(row=r(), column=0, sticky="E")
        ttk.Entry(f, textvar=v.length).grid(row=n(), column=1, sticky="EW")
        
        tk.Label(f, text="Duration of print:").grid(row=r(), column=0, sticky="E")
        _f = tk.Frame(f)
        ttk.Entry(_f, textvar=v.durationHr, width=5).grid(row=0, column=0, sticky="EW")
        tk.Label(_f, text="hr  ").grid(row=0, column=1, sticky="W")
        ttk.Entry(_f, textvar=v.durationMin, width=5).grid(row=0, column=2, sticky="EW")
        tk.Label(_f, text="min  ").grid(row=0, column=4, sticky="W")
        _f.columnconfigure((0,1,2), weight=1)
        _f.grid(row=n(), column=1, sticky="W")
        tk.Label(f, text="Printer:").grid(row=r(), column=0, sticky="E")
        ttk.Combobox(f, textvariable=v.printer, values=[p for p in self.printers]).grid(row=n(), column=1, sticky="EW")
        tk.Label(f, text="Print Rate:").grid(row=r(), column=0, sticky="E")
        ttk.Combobox(f, textvariable=v.rate, values=[r.rateid for r in self.rates]).grid(row=n(), column=1, sticky="EW")
        tk.Label(f, text="Notes (optional):").grid(row=n(), column=0, sticky="W")
        self.notesWid = tk.Text(f, width=50, height=5)
        self.notesWid.grid(row=n(), column=0, columnspan=2, sticky="EW")
        
        f.rowconfigure([i for i in range(f.grid_size()[1])], pad=2)
        f.columnconfigure([0,1], weight=1, pad=5)
        f.grid(row=1, column=0, sticky="EW")
        
        f = tk.Frame(content)
        ttk.Button(f, text="Submit", command=self.submit).grid(row=0, column=1, sticky="EW")
        ttk.Button(f, text="Cancel", command=self.cancel).grid(row=0, column=0, sticky="EW")
        f.columnconfigure((0,1), weight=1, pad=3)
        f.grid(row=2, column=0, sticky="EW")
        
        content.columnconfigure(0, weight=1)
        content.pack(fill="y", expand=True)
    
    
    def enablePayerEntry(self):
        if self.vars.isPayer.get():
            self.payeeEntry.config(state=tk.ACTIVE)
        else:
            self.payeeEntry.config(state=tk.DISABLED)
    
    
    def submit(self):
        # Validate input
        if not self.validate():
            return
        
        # Extract arguments for new print
        v = self.vars
        args = dict()
        args["userid"] = v.userid.get()
        args["passwd"] = v.passwd.get()
        
        rates = self.client.rate_get(name=v.rate.get())
        if rates:
            print(rates[0])
        else:
            print("No rate")
        args["rate"] = rates[0]
        
        args["printer"] = v.printer.get()
        if v.isPayer.get():
            args["paidby"] = v.payer.get()
        args["length"] = float(v.length.get())
        args["duration"] = int(v.durationHr.get())*60 + int(v.durationMin.get())
        if self.notesWid.get("1.0",'end-1c'):
            args["note"] = self.notesWid.get("1.0",'end-1c')
        
        # Get client to make print
        printjob = self.client.print_add(**args)
        if printjob:
            messagebox.showinfo("Success!", "Your Print ID is '{}'.".format(print.printid))
    
    
    def cancel(self):
        messagebox.showinfo("Info", "This feature hasn't been added yet.")
    
    
    """ Validate's the input. """
    def validate(self):
        # Let's make a list, problems, which we add to every time we find something wrong with the
        # input.
        problems = []
        
        v = self.vars
        
        # -- Check Formatting -----
        # Check if User ID is empty
        if not v.userid.get():
            problems.append("Your User ID must be given.")
        # Check if Password is empty
        if not v.passwd.get():
            problems.append("You must provide your password.")
        # Check if userid of payer is provided
        if v.isPayer.get() and not v.payer.get():
            problems.append("You indicated that someone else is paying, but didn't provide their User ID.")
        
        # Check that the length is given and that it is formatted correctly
        if not v.length.get():
            problems.append("You must specify how much fillament the print will use.")
        elif not isfloat(v.length.get()):
            problems.append("You must enter a numerical value for the approx. length of fillament.")
        elif float(v.length.get()) <= 0:
            problems.append("The approx. length of fillament must be greater tha zero.")
        # Check that the duration is given and formatted properly
        if not v.durationHr.get():
            problems.append("You must specify the approx. number of hours needed for the print (use 0 for times less than 1 hour).")
        elif not isint(v.durationHr.get()) or int(v.durationHr.get()) < 0:
            problems.append("The approx. number of hours needed for the print must be a positive integer.")
        if not v.durationMin.get():
            problems.append("You must specify the approx. number of minutes needed for the print.")
        elif not isint(v.durationMin.get()) or int(v.durationMin.get()) < 0 or int(v.durationMin.get()) > 59:
            problems.append("The approx. number of minutes must be an integer value between 0 and 59.")
        
        # Check Printer
        if not v.printer.get():
            problems.append("You must specify a printer.")
        if not v.rate.get():
            problems.append("You must specify a pricing rate for your print.")
        
        # Now, if we encountered any formatting errors, return False and display the problems.
        # Otherwise, move on.
        if problems:
            s = "The following formatting errors were found:\n\n"
            for p in problems:
                s += p + "\n"
            messagebox.showerror("Bad Input", s)
            return False
        
        # -- Check if the actual values are valid -----
        # User ID and Password
        if not self.client.user_verify(v.userid.get(), v.passwd.get()):
            messagebox.showerror("Bad Login", "Your User ID and password are invalid.")
            return False
        if v.isPayer.get() and not self.client.user_get(userid=v.payer.get()):
            messagebox.showerror("Bad User ID", "No user exists with the ID '{}'.".format(v.payer.get()))
            return False
        
        # Make sure the duration isn't too short
        if int(v.durationHr.get())*60 + int(v.durationMin.get()) < 1:
            messagebox.showerror("Bad Input", "The specified duration is impossibly short. C'mon, be reasonable.")
            return False
        
        # -- Return True if nothing has been caught -----
        return True
        
        


###################################################################################################
# ListPrinterPage                                                                 ListPrinterPage #
class ListPrinterPage(tk.Frame):
    # --------------------------------------------------------- ListPrinterPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        
        self.addWidgets()
        self.refreshTree()
    
    
    # --------------------------------------------------------- ListPrinterPage ---- addWidgets() #
    def addWidgets(self):
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="Add New Printer", width=20, command=self.add).pack(side="top")
        ttk.Button(f, text="Rename Printer", width=20, command=self.edit).pack(side="top")
        ttk.Button(f, text="Delete Printer", width=20, command=self.delete).pack(side="top")
        f.pack(side="right", fill="y")
        
        # Add List
        f = tk.Frame()
        columns = ("printer",)
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.column("printer", width=100, anchor="w")
        self.tree.heading("printer", text="Printer", command=lambda: self.sort(0))
        self.tree.pack(fill="both")
        f.pack(side="left", fill="both")
    
    
    # --------------------------------------------------------- ListPrinterPage --- refreshTree() #
    def refreshTree(self):
        # Get list of printers
        try:
            printers = self.client.printer_get()
        except Exception as e:
            messagebox.showerror("Error", 
                                 "An error occurred while getting printer data.\n\n{}".format(str(e)))
        
        self.tree.delete(*self.tree.get_children())
        for p in printers:
            vals = (p,)
            self.tree.insert("", 0, text="", values=vals)
    
    
    # --------------------------------------------------------- ListPrinterPage ---------- sort() #
    """ Rearranges the items in the tree. """
    def sort(self, col):
        items = self.tree.get_children("")
        f = lambda x: self.tree.item(x, "values")[col]
        sorted = [item for item in natsort.natsorted(items, key=f)]
        
        for id in sorted:
            self.tree.move(id, "", "end")
    
    
    # --------------------------------------------------------- ListPrinterPage ----------- add() #
    """ Opens page for creating a new print rate. """
    def add(self):
        auth_userid, auth_passwd = UserVerify.getLogin(self)
        if not self.client.user_issuper(auth_userid, auth_passwd):
            messagebox.showerror("Invalid Login", "That user is not allowed to edit printers.")
            return
        
        name = EntryPopup.getText(self, "Add Printer", "Enter the name of the new printer.")
        try:
            self.client.printer_add(name, auth_userid, auth_passwd)
            messagebox.showinfo("Success", "Printer added successfully.")
            self.refreshTree()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    
    # --------------------------------------------------------- ListPrinterPage ---------- edit() #
    """ Opens an editing page for the print rate. """
    def edit(self):
        pass
    
    
    # --------------------------------------------------------- ListPrinterPage ---------- edit() #
    """ Prompts the user for authentication, and if valid, deletes the selected print. """
    def delete(self):
        if len(self.tree.selection()) == 0:
            return
        printer = self.tree.item(self.tree.selection()[0], "values")[0]
        
        # Get Verification
        auth_userid, auth_passwd = UserVerify.getLogin(self)
        if not self.client.user_issuper(auth_userid, auth_passwd):
            messagebox.showerror("Bad Login", "That user ({}) is not allowed to delete printers.".format(auth_userid))
        else:
            try:
                self.client.printer_delete(printer, auth_userid, auth_passwd)
                messagebox.showinfo("Success", "The printer '{}' was successfully removed.".format(printer))
                self.refreshTree()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        


###################################################################################################
# AddFailedPage                                                                     AddFailedPage #
class AddFailedPage(tk.Frame):
    # ----------------------------------------------------------- AddFailedPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        
        self.app = parent
        while not isinstance(self.app, App):
            self.app = self.app.parent
        
        self.userid, self.passwd = UserVerify.getLogin(self)
        if not self.client.user_verify(self.userid, self.passwd):
            messagebox.showerror("Bad Login", "The username or password is incorrect.")
            self.app.openFrame("Start")
        
        self.vars = struct()
        self.vars.userid = tk.StringVar(value=self.userid)
        self.vars.printid = tk.StringVar()
        self.vars.completion = tk.DoubleVar()
        
        self.addWidgets()
        self.refresh()
    
    
    # ----------------------------------------------------------- AddFailedPage ---- addWidgets() #
    def addWidgets(self):
        v = self.vars
        
        f = tk.Frame(self, width=500)
        
        tk.Label(f, text="User ID:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.userid).grid(row=0, column=1, sticky="EW")
        ttk.Button(f, text="Refresh", command=self.refresh).grid(row=1, column=1)
        tk.Label(f, text="Print ID:").grid(row=2, column=0, sticky="E")
        self.combo = ttk.Combobox(f, textvariable=v.printid)
        self.combo.grid(row=2, column=1, sticky="EW")
        tk.Label(f, text="% Completion").grid(row=3, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.completion).grid(row=3, column=1, sticky="EW")
        ttk.Button(f, text="Add Failed Print", command=self.submit).grid(row=5, column=1, sticky="EW")
        ttk.Button(f, text="Cancel", command=self.cancel).grid(row=5, column=0, sticky="EW")
        
        f.columnconfigure((0,1), weight=1, pad=5)
        f.rowconfigure((0,1,2,3,4,5), weight=1, pad=2)
        
        f.pack()
    
    
    # ----------------------------------------------------------- AddFailedPage ------- refresh() #
    def refresh(self):
        if not self.client.user_get(userid=self.vars.userid.get()):
            messagebox.showerror("No user exists with that ID.")
            return
        if not self.client.user_issuper(self.userid, self.passwd):
            messagebox.showerror("You are not allowed to add failed prints to another user.")
            return
        
        self.prints = self.client.print_get(userid=self.vars.userid.get(), finished=False)
        self.printids = [p.printid for p in self.prints]
        self.combo["values"] = self.printids
    
    
    # ----------------------------------------------------------- AddFailedPage -------- verify() #
    def verify(self):
        problems = [] # List to hold info about any formatting errors
        
        v = self.vars
        if not v.userid.get():
            problems.append("You must enter a User ID.")
        elif not self.client.user_get(userid=v.userid.get()):
            problems.append("No user ecists with the specified ID.")
        if not v.printid.get():
            problems.append("You must choose a printid.")
        elif not self.client.print_get(printid=v.printid.get()):
            problems.append("No print exists with that Print ID.")
        if not isfloat(v.completion.get()) or not 0 <= float(v.completion.get()) <= 100:
            problems.append("The % completion must be a number between 0 and 100.")
        
        # Display a helpful message if there were any formatting errors
        if problems:
            msg = ""
            for s in ["The following formatting errors were found.:"] + problems:
                msg += s + "\n"
            messagebox.showerror("Bad Input", msg)
        
        # Return whether or not there were errors
        return not problems
    
    
    # ----------------------------------------------------------- AddFailedPage -------- submit() #
    def submit(self):
        # Check input
        if not self.verify():
            return
        
        # Add Failed Print
        percent = float(self.vars.completion.get())/100
        p = self.client.print_get(printid=self.vars.printid.get())[0]
        length = percent * p.length
        duration = int(percent * p.duration)
        
        self.client.print_add_failed(printid=p.printid, length=length, duration=duration)
        messagebox.showinfo("Success", "Failed print added.")
    
    
    # ----------------------------------------------------------- AddFailedPage -------- cancel() #
    def cancel(self):
        self.app.openFrame("Start")
        


###################################################################################################
# ListRatePage                                                                       ListRatePage #
class ListRatePage(tk.Frame):
    # ------------------------------------------------------------ ListRatePage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        
        self.addWidgets()
        self.refreshTree()
    
    
    # ------------------------------------------------------------ ListRatePage ---- addWidgets() #
    def addWidgets(self):
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="Add New Rate", width=20, command=self.add).pack(side="top")
        ttk.Button(f, text="Edit Rate", width=20, command=self.edit).pack(side="top")
        ttk.Button(f, text="Delete Rate", width=20).pack(side="top")
        f.pack(side="right", fill="y")
        
        # Add List
        f = tk.Frame()
        columns = ("rateid", "lengthrate", "timerate",)
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.column("rateid", width=100, anchor="w")
        self.tree.heading("rateid", text="Rate", command=lambda: self.sort(0))
        self.tree.column("lengthrate", width=100, anchor="w")
        self.tree.heading("lengthrate", text="$/m", command=lambda: self.sort(1))
        self.tree.column("timerate", width=100, anchor="w")
        self.tree.heading("timerate", text="$/hr", command=lambda: self.sort(2))
        self.tree.pack(fill="both")
        f.pack(side="left", fill="both")
    
    
    # ------------------------------------------------------------ ListRatePage --- refreshTree() #
    def refreshTree(self):
        # Get list of rates
        try:
            rates = self.client.rate_get()
        except Exception as e:
            messagebox.showerror("Error", 
                                 "An error occurred while getting rate data.\n\n{}".format(str(e)))
        
        self.tree.delete(*self.tree.get_children())
        for r in rates:
            vals = (r.name, r.lengthrate, r.timerate)
            self.tree.insert("", 0, text="", values=vals)
    
    
    # ------------------------------------------------------------ ListRatePage ---------- sort() #
    """ Rearranges the items in the tree. """
    def sort(self, col):
        items = self.tree.get_children("")
        f = lambda x: self.tree.item(x, "values")[col]
        sorted = [item for item in natsort.natsorted(items, key=f)]
        
        for id in sorted:
            self.tree.move(id, "", "end")
    
    
    # ------------------------------------------------------------ ListRatePage ----------- add() #
    """ Opens page for creating a new print rate. """
    def add(self):
        self.parent.openFrame("AddRate")
    
    
    # ------------------------------------------------------------ ListRatePage ---------- edit() #
    """ Opens an editing page for the print rate. """
    def edit(self):
        pass


###################################################################################################
# AddRatePage                                                                         AddRatePage #
class AddRatePage(tk.Frame):
    # ------------------------------------------------------------- AddRatePage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.client = parent.client
        self.vars = struct()
        
        self.addWidgets()
    
    # ------------------------------------------------------------- AddRatePage ---- addWidgets() #
    def addWidgets(self):
        v = self.vars
        v.rateid = tk.StringVar()
        v.name = tk.StringVar()
        v.lengthrate = tk.StringVar()
        v.timerate = tk.StringVar()
        
        f = tk.Frame(self, width=200)
        f.columnconfigure((0,1), weight=1, pad=5)
        tk.Label(f, text="Name: ").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.name).grid(row=0, column=1, sticky="EW")
        tk.Label(f, text="ID Code: ").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.rateid).grid(row=1, column=1, sticky="EW")
        tk.Label(f, text="$/m: ").grid(row=2, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.lengthrate).grid(row=2, column=1, sticky="EW")
        tk.Label(f, text="$/hr: ").grid(row=3, column=0, sticky="E")
        ttk.Entry(f, textvariable=v.timerate).grid(row=3, column=1, sticky="EW")
        ttk.Button(f, text="Cancel").grid(row=4, column=0, sticky="E")
        ttk.Button(f, text="Save", command=self.submit).grid(row=4, column=1, sticky="W")
        f.pack(fill="y")
    
    
    # ------------------------------------------------------------- AddRatePage -------- submit() #
    def submit(self):
        v = self.vars
        if self.client.rate_get(rateid=v.rateid.get()):
            messagebox.error("Bad Input", "This Rate ID is already in use. Please choose another ID.")
        elif not isfloat(v.lengthrate.get()):
            messagebox.showerror("BAd Input", "The value for the length rate is not valid numerical input.")
        elif not isfloat(v.timerate.get()):
            messagebox.showerror("Bad Input", "The value for the time rate is not valid numerical input.")
        else:
            auth_userid, auth_passwd = UserVerify.getLogin(self)
            if self.client.user_issuper(auth_userid, auth_passwd):
                self.client.rate_add(v.rateid.get(), float(v.lengthrate.get()), 
                                     float(v.timerate.get()), v.name.get(), auth_userid, auth_passwd)
                self.parent.openFrame("ListRates")
            else:
                messagebox.showerror("Login Error", "Invalid login.")
            
        
        
        
###################################################################################################
# ListUserPage                                                                       ListUserPage #
class ListUserPage(tk.Frame):
    # ------------------------------------------------------------ ListUserPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.addWidgets()
        self.refreshTree()
    
    
    # ------------------------------------------------------------ ListUserPage ---- addWidgets() #
    def addWidgets(self):
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="Edit User", width=20, command=self.edit).pack(side="top")
        ttk.Button(f, text="Delete User", width=20).pack(side="top")
        f.pack(side="right", fill="y")
        
        # Add List
        f = tk.Frame()
        columns = ("userid", "lastname", "firstname", "email", "issuper",)
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.column("userid", width=100, anchor="w")
        self.tree.heading("userid", text="User ID", command=lambda: self.sort(1))
        self.tree.column("firstname", width=100, anchor="w")
        self.tree.heading("firstname", text="First Name", command=lambda: self.sort(2))
        self.tree.column("lastname", width=100, anchor="w")
        self.tree.heading("lastname", text="Last Name", command=lambda: self.sort(3))
        self.tree.column("email", width=100, anchor="w")
        self.tree.heading("email", text="E-mail", command=lambda: self.sort(4))
        self.tree.column("issuper", width=50, anchor="w")
        self.tree.heading("issuper", text="Is mod?", command=lambda: self.sort(5))
        self.tree.pack(fill="both")
        f.pack(side="left", fill="both")
    
    
    # ------------------------------------------------------------ ListUserPage --- refreshTree() #
    def refreshTree(self):
        # Get list of users
        try:
            users = self.parent.client.user_get()
        except Exception as e:
            messagebox.showerror("Error", "An error occurred while getting user data.\n\n{}".format(str(e)))
            return
        print(type(users))
        self.tree.delete(*self.tree.get_children())
        for u in users:
            vals = (u.userid, u.firstname, u.lastname, u.email, str(u.issuper))
            self.tree.insert("", 0, text="", values=vals)
    
    
    # ------------------------------------------------------------ ListUserPage ---------- sort() #
    """ Rearranges the items in the tree. """
    def sort(self, col):
        items = self.tree.get_children("")
        f = lambda x: self.tree.item(x, "values")[col]
        sorted = [item for item in natsort.natsorted(items, key=f)]
        
        for id in sorted:
            self.tree.move(id, "", "end")
    
    
    # ------------------------------------------------------------ ListUserPage ---------- edit() #
    """ Opens the edit user screen. """
    def edit(self):
        # If no user is selected, then do nothing
        if len(self.tree.selection()) == 0:
            return
        userid = self.tree.item(self.tree.selection()[0], "values")[0]
        
        # Else, get some info to see who is trying to edit this user
        msg = "To edit this user, please provide your login details."
        who_id, who_pass = UserVerify.getLogin(self, message=msg)
        
        # If no login info was entered, just quit
        if not who_id or not who_pass:
            return
        
        logger.debug("edit: User is {}".format(who_id))
        
        # If the user is editing their own profile, then verify their credentials. Otherwise, make
        # sure the user is a mod before allowing them to edit the profile.
        
        verified = False
        try:
            verified = self.parent.client.user_verify(who_id, who_pass)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        
        if not verified:
            messagebox.showerror("Bad Login", "Your login was incorrect. Are you sure you used the correct password?")
            return
        elevated = self.parent.client.user_issuper(who_id, who_pass)
        if not who_id == userid and not elevated:
            messagebox.showerror("Access Denied", "You do not have permission to edit this user.")
        elif not self.parent.client.user_get(userid):
            messagebox.showerror("Error", "Can't edit this user - apparently it doesn't exist.")
        else:
            auth = (who_id, who_pass)
            self.parent.openFrame("EditUser", userid=userid, elevated=elevated, auth=auth)
            
    
###################################################################################################
# UserVerify                                                                           UserVerify #
class UserVerify(tk.Toplevel):
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
        e = ttk.Entry(f, textvariable=self.entry1)
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
        self.destroy()
    
    
    # -------------------------------------------------------------- UserVerify -------- cancel() #
    def cancel(self):
        self.destroy()
    
    
    # -------------------------------------------------------------- UserVerify ------ getLogin() #
    def getLogin(parent, message="Please enter your login information.", userid=""):
        win = UserVerify(message, userid)
        uservar = win.userid
        passvar = win.passwd
        win.grab_set()
        parent.wait_window(win)
        return (uservar.get(), passvar.get())


class EntryPopup(tk.Toplevel):
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
    
    def submit(self):
        self.destroy()
    
    def cancel(self):
        self.text.set("")
        self.destroy()
    
    def getText(root, title=None, message=None):
        top = EntryPopup(root, title=title, message=message)
        text = top.text
        top.grab_set()
        top.wait_window()
        return text.get()


# A nice class for keeping track of rownums
class rn:
    def __init__(self, start=0):
        self.r = 0
    
    def row(self):
        return self.r

    def new(self):
        self.r += 1
        return self.r-1
    
    def reset(self, start=0):
        self.r = start


# Class for entry text validation
class Validate:
    lower = "qwertyuiopasdfghjklzxcvbnm"
    upper = lower.upper()
    digits = "0123456789"
    numerical = digits + "."
    symbols = r"&^*$%!@#_"
    
    def alpha(txt):
        for char in txt:
            if char not in upper+lower:
                return False
        return True
    
    def alphanumeric(txt):
        for char in txt:
            if char not in upper+lower+digits:
                return False
        return True

    def numeric(txt):
        for char in txt:
            if char not in digits:
                return False
        return True
    
    def decimal(txt):
        for char in txt:
            if char not in numerical:
                return False
        if txt.count(".") > 1:
            return False
        return True
    
    def userid(txt):
        for char in txt:
            if char not in lower+upper+numerical+symbols:
                return False
        return True
        
    
        
        
        
        
        


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.title("Logger")
    root.geometry('{}x{}'.format(WIDTH, HEIGHT))
    root.protocol("WM_DELETE_WINDOW", app.onExit)
    root.mainloop()
    