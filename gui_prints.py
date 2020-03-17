# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:36:25 2020

@author: Ben
"""

###################################################################################################
# IMPORTS                                                                                 IMPORTS #
# -- System Modules -- #
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg

# -- Third Party -- #
import natsort as ns

# -- Custom -- #
from benutil import struct, isfloat, isint
from gui_framework import App, Page, UserVerify, rn, TableView


###################################################################################################
# ListPrintsPage                                                                   ListPrintsPage #
class ListPrintsPage(Page):
    # -- Class Attributes -- #
    title = "Prints"
    
    # ---------------------------------------------------------- ListPrintsPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        self.prints = self.client.print_get()
        self.rates = ns.natsorted(self.client.rate_get(), key=lambda x: x.name)
        
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
        ttk.Button(f, text="Mark as Finished", width=20, command=self.finish).pack(side="top")
        ttk.Button(f, text="Filter", width=20, command=self.filt).pack(side="bottom")
        f.pack(side="right", fill="y")
        
        # Add List
        f = tk.Frame(self)
        columns = ("printid", "userid", "date", "cost", "rate", "printer", "length", "duration", "finished")
        '''self.tree = ttk.Treeview(f, columns=columns, show="headings", selectmode="browse")
        self.tree.column("printid", width=150, anchor="w")
        self.tree.heading("printid", text="Print ID", command=lambda: self.sort(0))
        self.tree.column("userid", width=100, anchor="w")
        self.tree.heading("userid", text="User ID", command=lambda: self.sort(1))
        self.tree.column("date", width=150, anchor="w")
        self.tree.heading("date", text="Date Logged", command=lambda: self.sort(2))
        self.tree.column("cost", width=100, anchor="w")
        self.tree.heading("cost", text="Cost", command=lambda: self.sort(3))
        self.tree.column("rate", width=100, anchor="w")
        self.tree.heading("rate", text="Pricing Rate", command=lambda: self.sort(4))
        self.tree.column("printer", width=100, anchor="w")
        self.tree.heading("printer", text="Printer", command=lambda: self.sort(5))
        self.tree.column("length", width=100, anchor="w")
        self.tree.heading("length", text="Length", command=lambda: self.sort(6))
        self.tree.column("duration", width=100, anchor="w")
        self.tree.heading("duration", text="Duration", command=lambda: self.sort(7))
        self.tree.column("finished", width=100, anchor="w")
        self.tree.heading("finished", text="Finished?", command=lambda: self.sort(8))'''
        self.tree = TableView(f, columns=columns, selectmode="browse")
        self.tree.pack(fill="both", expand="true")
        
        hsb = ttk.Scrollbar(f, orient="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=hsb.set)
        f.pack(fill="both", expand="true")
        
        # Filtering
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
    
    
    # ---------------------------------------------------------- ListPrintsPage --- refreshTree() #
    def refreshTree(self, prints):
        # Get list of users
        '''self.tree.delete(*self.tree.get_children())
        for p in prints:
            print(p.failedPrints)
            vals = (p.printid, p.userid, p.date.strftime("%Y-%m-%d\t%H:%M:%S"), "${:.2f}".format(p.calcCost()), 
                    p.rate.name, p.printer, str(p.length) + " m", str(p.duration) + " min",
                    p.finished)
            self.tree.insert("", 0, text="", values=vals)'''
        self.tree.empty()
        for p in prints:
            date = p.date.strftime("%Y-%m-%d %H:%M:%S")
            amt = "${:.2f}".format(p.calcCost())
            length = "{} m".format(p.length)
            duration = "{:.0f}hr {:.0f}min".format(p.duration // 60, p.duration % 60)
            self.tree.addRow((p, p.printid, p.userid, date, amt, p.rate.name, p.printer, length, 
                              duration, p.finished))
    
    
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
            msg.showerror("Bad Input", msg)
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
    
    
    # ---------------------------------------------------------- ListPrintsPage -------- finish() #
    """ Marks the selected print as 'finished'. """
    def finish(self):
        # If no print is selected, then do nothing
        if len(self.tree.selection()) == 0:
            return
        '''p = self.tree.item(self.tree.selection()[0], "values")[0]'''
        p = self.tree.getRows()[0][0]
        
        printjob = self.client.print_get(printid=p.printid)[0]
        
        # Get Login
        status, code, userid, passwd = UserVerify.verifyLogin(self, printjob.userid)
        if not status:
            if code == UserVerify.BAD_LOGIN:
                msg.showerror("Bad Login", "Login info is incorrect.")
            if code == UserVerify.WRONG_USER:
                msg.showerror("Bad Login", "You do not have permission to edit this print.")
        else:
            msg.showinfo("Edit Print", "This print has been marked as 'finished'.")
            self.client.print_edit(printjob, finished=True)
            self.filt()
    
    
    # ---------------------------------------------------------- ListPrintsPage ---------- edit() #
    def edit(self, *args, **kwargs):
        # If no print is selected, then do nothing
        if len(self.tree.selection()) == 0:
            return
        p = self.tree.getRows()[0][0]
        
        # Begin editing
        App.app.openFrame("EditPrint", printjob=p)
    
    
    # ---------------------------------------------------------- ListPrintsPage -------- delete() #
    def delete(self):
        p = self.tree.getRows()[0][0]
        
        # Get Authorization
        status, code, userid, passwd = UserVerify.verifyLogin(self, p.userid)
        if not status:
            if code == UserVerify.BAD_LOGIN:
                msg.showerror("Bad Login", "Login info is incorrect.")
            if code == UserVerify.WRONG_USER:
                msg.showerror("Bad Login", "You do not have permission to delete this print.")
        
        printid = p.printid
        self.client.print_delete(printid, userid, passwd)
        self.filt()


###################################################################################################
# AddPrintPage                                                                       AddPrintPage #
class AddPrintPage(Page):
    # -- Class Attributes -- #
    title = "App Print"
    
    # ------------------------------------------------------------ AddPrintPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
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
        ttk.Button(f, text="Submit", command=self.submit, underline=0).grid(row=0, column=1, sticky="EW")
        ttk.Button(f, text="Cancel", command=self.cancel, underline=0).grid(row=0, column=0, sticky="EW")
        f.columnconfigure((0,1), weight=1, pad=3)
        f.grid(row=2, column=0, sticky="EW")
        
        content.columnconfigure(0, weight=1)
        content.pack(fill="y", expand=True)
        
        self.bind("<Control-s>", lambda e: self.submit)
        self.bind("<Control-c>", lambda e: self.cancel)
    
    
    # ------------------------------------------------------------ AddPrintPageenablePayerEntry() #
    def enablePayerEntry(self):
        if self.vars.isPayer.get():
            self.payeeEntry.config(state=tk.ACTIVE)
        else:
            self.payeeEntry.config(state=tk.DISABLED)
    
    
    # ------------------------------------------------------------ AddPrintPage -------- submit() #
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
            msg.showinfo("Success!", "Your Print ID is '{}'.".format(printjob.printid))
    
    # ------------------------------------------------------------ AddPrintPage -------- cancel() #
    def cancel(self):
        App.app.openFrame("Start")
    
    
    # ------------------------------------------------------------ AddPrintPage ------ validate() #
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
        
        # Check Printer and Rate
        if not v.printer.get():
            problems.append("You must specify a printer.")
        elif v.printer.get() not in self.client.printer_get():
            problems.append("Invalid printer choice.")
        if not v.rate.get():
            problems.append("You must specify a pricing rate for your print.")
        elif v.rate.get() not in [r.rateid for r in self.client.rate_get()]:
            problems.append("Invalid pricing rate choice.")
        
        # Now, if we encountered any formatting errors, return False and display the problems.
        # Otherwise, move on.
        if problems:
            s = "The following formatting errors were found:\n\n"
            for p in problems:
                s += p + "\n"
            msg.showerror("Bad Input", s)
            return False
        
        # -- Check if the actual values are valid -----
        # User ID and Password
        if not self.client.user_verify(v.userid.get(), v.passwd.get()):
            msg.showerror("Bad Login", "Your User ID and password are invalid.")
            return False
        if v.isPayer.get() and not self.client.user_get(userid=v.payer.get()):
            msg.showerror("Bad User ID", "No user exists with the ID '{}'.".format(v.payer.get()))
            return False
        
        # Make sure the duration isn't too short
        if int(v.durationHr.get())*60 + int(v.durationMin.get()) < 1:
            msg.showerror("Bad Input", "The specified duration is impossibly short. C'mon, be reasonable.")
            return False
        
        # -- Return True if nothing has been caught -----
        return True


###################################################################################################
# EditPrintPage                                                                     EditPrintPage #
class EditPrintPage(Page):
    # -- Class Attributes -- #
    title = "Edit Print"
    
    # ----------------------------------------------------------- EditPrintPage ------ __init__() #
    def __init__(self, parent, printjob, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        # Get Verification. Only admit people who are moderators or who already own the print.
        status, code, userid, passwd = UserVerify.verifyLogin(self, target=printjob.userid)
        if not status:
            if code == UserVerify.BAD_LOGIN:
                msg.showerror("Bad Login", "Your login info is incorrect. Please try again.")
            elif code == UserVerify.WRONG_USER:
                msg.showerror("Bad Login", "You don't have permission to access this print.")
            self.abort = True
            return
        
        self.rates = self.client.rate_get()
        self.printers = self.client.printer_get()
        
        # Create Tk Variables
        self.vars = struct()
        v = self.vars
        v.userid = tk.StringVar(value=printjob.userid)
        v.notPayer = tk.IntVar(value=printjob.paidBy != printjob.userid)
        v.payer = tk.StringVar(value=printjob.paidBy)
        v.length = tk.StringVar(value=printjob.length)
        v.durationHr = tk.StringVar(value=printjob.duration//60)
        v.durationMin = tk.StringVar(value=printjob.duration%60)
        v.rate = tk.StringVar(value=printjob.rate.name)
        v.printer = tk.StringVar(value=printjob.printer)
        v.finished = tk.IntVar(value=printjob.finished)
        
        self.printjob = printjob
        self.addWidgets()
    
    
    # ----------------------------------------------------------- EditPrintPage ---- addWidgets() #
    def addWidgets(self):
        v = self.vars
        rownum = rn()
        r = rownum.row
        n = rownum.new
        
        content = tk.Frame(self, width=500)
        
        # User and Billing Info
        f = ttk.Labelframe(content, text="User Info", width=500)
        tk.Label(f, text="User ID").grid(row=r(), column=0, sticky="E")
        ttk.Entry(f, textvar=v.userid, state=tk.DISABLED).grid(row=n(), column=1, sticky="EW")
        
        ttk.Checkbutton(f, text="Is a different user paying for this print?", 
                        variable=v.notPayer, command=self.ev_checkbox).grid(row=n(), column=0, 
                                                                            columnspan=2)
        tk.Label(f, text="User ID").grid(row=r(), column=0, sticky="E")
        self.payeeEntry = ttk.Entry(f, textvar=v.payer)
        if not self.vars.notPayer.get():
            self.payeeEntry.config(state="disabled")
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
        
        ttk.Checkbutton(f, text="Is this print finished?", 
                        variable=v.finished).grid(row=n(), column=0, columnspan=2)
        
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
    
    
    def ev_checkbox(self):
        if not self.vars.notPayer.get():
            self.payeeEntry.config(state="disabled")
        else:
            self.payeeEntry.config(state="normal")
    
    
    def submit(self):
        v = self.vars
        if self.vars.notPayer.get():
            paidBy = v.payer.get()
        else:
            paidBy = v.userid.get()
        length = float(v.length.get())
        duration = int(v.durationHr.get())*60 + int(v.durationMin.get())
        rate = self.client.rate_get(name=v.rate.get())[0]
        printer = v.printer.get()
        finished = bool(v.finished.get())
        
        self.client.print_edit(self.printjob, paidBy=paidBy, length=length, duration=duration, rate=rate,
                               printer=printer, finished=finished)
        msg.showinfo("Success", "Your changes have been saved.")
        App.app.openFrame("ListPrints")
    
    def cancel(self):
        App.app.openFrame("ListPrints")


###################################################################################################
# AddFailedPage                                                                     AddFailedPage #
class AddFailedPage(Page):
    # -- Class Attributes -- #
    title = "Add Failed Print"
    
    # ----------------------------------------------------------- AddFailedPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        # Get login before opening screen. We ask for login so that we can display only prints
        # belonging to the actual user
        status, code, self.userid, self.passwd = UserVerify.verifyLogin(self)
        self.issuper = self.client.user_issuper(self.userid, self.passwd)
        if not status:
            if code == UserVerify.BAD_LOGIN:
                msg.showerror("Bad Login", "Your login info is incorrect. Please try again.")
            self.abort = True
            return
        
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
        e_userid = ttk.Entry(f, textvariable=v.userid)
        if not self.issuper:
            e_userid["state"] = "disabled"
        e_userid.grid(row=0, column=1, sticky="EW")
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
            msg.showerror("Bad User ID", "No user exists with that ID.")
            return
        if self.vars.userid.get() != self.userid and not self.client.user_issuper(self.userid, self.passwd):
            msg.showerror("Permission Denied", "You are not allowed to add failed prints to another user.")
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
            m = ""
            for s in ["The following formatting errors were found.:"] + problems:
                m += s + "\n"
            msg.showerror("Bad Input", m)
        
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
        m = ["Failed print added."]
        m.append("")
        m.append("Print ID: {}".format(p.printid))
        m.append("User ID: {}".format(p.userid))
        msg.showinfo("Success", "\n".join(m))
    
    
    # ----------------------------------------------------------- AddFailedPage -------- cancel() #
    def cancel(self):
        App.app.openFrame("Start")