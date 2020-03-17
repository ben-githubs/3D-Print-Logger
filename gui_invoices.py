# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 17:17:17 2020

@author: Ben
"""

###################################################################################################
# IMPORTS                                                                                 IMPORTS #
# -- System Modules -- #
from configparser import ConfigParser
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# -- Custom -- #
from benutil import struct, isfloat, isint, isdate, datefstr
from gui_framework import App, Page, UserVerify, TableView, EntryPopup
from makerspace import ServerError


###################################################################################################
# ListInvoicePage                                                                 ListInvoicePage #
class ListInvoicePage(Page):
    # -- Class Attributes -- #
    title = "Invoices"
    
    # --------------------------------------------------------- ListInvoicePage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        # Load Invoices
        self.invs = self.client.invoice_get()
        
        # Prapare GUI variables for data aquisition
        self.vars = struct()
        v = self.vars
        v.userid = tk.StringVar()
        v.dateMin = tk.StringVar()
        v.dateMax = tk.StringVar()
        
        # Set up GUI
        self.addWidgets()
        self.refreshTree()
        self.tree.sort(0)
        
        # Load Config
        self.conf = ConfigParser()
        self.conf.read("client.ini")
    
    
    # --------------------------------------------------------- ListInvoicePage ---- addWidgets() #
    def addWidgets(self):
        v = self.vars
        
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="View Invoice", width=20, command=self.view).pack(side="top")
        ttk.Button(f, text="Export CSV", width=20, command=self.exportCsv).pack(side="top")
        ttk.Button(f, text="Export HTML", width=20, command=self.exportHtml).pack(side="top")
        ttk.Button(f, text="Filter", width=20, command=self.filt).pack(side="bottom")
        f.pack(side="right", fill="y")
        
        # Add List
        f = tk.Frame(self)
        self.tree = TableView(f, columns=("Invoice ID", "User ID", "Date", "Cost"), selectmode="browse")
        [self.tree.column(i, width=100) for i in range(4)]
        
        hsb = ttk.Scrollbar(f, orient="horizontal", command=self.tree.xview)
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        hsb.grid(row=1, column=0, sticky="EW")
        vsb.grid(row=0, column=1, sticky="NS")
        self.tree.grid(row=0, column=0, sticky="NEWS")
        self.tree.configure(xscrollcommand=hsb.set)
        self.tree.configure(yscrollcommand=vsb.set)
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=0)
        f.pack(fill="both", expand="true")
        
        # Filtering
        f = tk.Frame(self)
        tk.Label(f, text="User: ").grid(row=0, column=0, sticky="E")
        ttk.Combobox(f, textvariable=v.userid, values=self.client.user_get()).grid(row=0, column=1, sticky="EW")
        tk.Label(f, text="Date (Start): ").grid(row=0, column=2, sticky="E")
        ttk.Entry(f, textvariable=v.dateMin).grid(row=0, column=3, sticky="EW")
        tk.Label(f, text="Date (End): ").grid(row=1, column=2, sticky="E")
        ttk.Entry(f, textvariable=v.dateMax).grid(row=1, column=3, sticky="EW")
        f.pack(fill="x")
    
    
    # --------------------------------------------------------- ListInvoicePage ---------- filt() #
    def filt(self):
        pass
    
    
    # --------------------------------------------------------- ListInvoicePage ---------- view() #
    def view(self):
        # Get invid of specified invoice
        if len(self.tree.selection()) == 0:
            return
        invid = self.tree.getRows()[0][0]
        
        # Open invoice in new frame
        try:
            inv = self.client.invoice_get(invid=str(invid))
            App.app.openFrame("ViewInvoice", inv)
        except ServerError as e:
            s = "".join(["An error occured on the server while processing your request.", "\n\n",
                         "Error Message: ", str(e)])
            messagebox.showerror("Server Error", s)
        except Exception as e:
            s = "".join(["An unknown error occured while procesing your request.\n\n",
                         "Error Message: ", str(e)])
            messagebox.showerror("Error", s)
    
    
    # --------------------------------------------------------- ListInvoicePage --- refreshTree() #
    def refreshTree(self):
        self.tree.empty()
        for i in self.invs:
            self.tree.addRow((i, i.invid, i.userid, i.date.isoformat(),
                              "${:.2f}".format(i.calcCost())))
    
    
    # --------------------------------------------------------- ListInvoicePage ----- exportCsv() #
    def exportCsv(self):
        try:
            # Get the invoice
            rows = self.tree.getRows()
            if len(rows) == 0: # If nothing is selected, return
                return
            inv = rows[0][0]
            # Prompt where to save the exported file
            initdir = self.conf.get("FILES", "invoice csv last saved", fallback="C:\\")
            title = "Save CSV As"
            ft = ("CSV Files", "*.csv"), ("All Files", "*.*")
            fname = filedialog.asksaveasfilename(initialdir=initdir, title=title, filetypes=ft)
            # Cancel if user exists dialog
            if not fname:
                return
            # Add CSV if not included
            if "." not in fname:
                fname += ".csv"
            # Write the file
            with open(fname, "w+") as f:
                f.write(inv.exportCSV())
            # Save path to config
            self.conf.set("FILES", "invoice csv last saved", os.path.split(fname)[0])
        except Exception as e:
            messagebox.showerror("Error", "An unknown error occured during export.\n\n"+str(e))
            return
        messagebox.showinfo("Invoice Exported Successfully", "Invoice Exported!")
    
    
    # --------------------------------------------------------- ListInvoicePage ---- exportHtml() #
    def exportHtml(self):
        try:
            # Get the invoice
            rows = self.tree.getRows()
            if len(rows) == 0: # If nothing is selected, return
                return
            inv = rows[0][0]
            # Prompt where to save the exported file
            initdir = self.conf.get("FILES", "invoice html last saved", fallback="C:\\")
            title = "Save HTML As"
            ft = ("HTML Files", "*.html"), ("All Files", "*.*")
            fname = filedialog.asksaveasfilename(initialdir=initdir, title=title, filetypes=ft)
            # Save path to config
            self.conf.set("FILES", "invoice html last saved", os.path.split(fname)[0])
            # Cancel if user exits dialog
            if not fname:
                return
            # Add CSV if not included
            if "." not in fname:
                fname += ".html"
            # Write the file
            user = self.client.user_get(userid=inv.userid)[0]
            with open(fname, "w+") as f:
                f.write(inv.exportHTML(user))
        except Exception as e:
            messagebox.showerror("Error", "An unknown error occured during export.\n\n"+str(e))
            return
        messagebox.showinfo("Invoice Exported Successfully", "Invoice Exported!")


###################################################################################################
# AddInvoicePage                                                                   AddInvoicePage #
class AddInvoicePage(Page):
    # -- Class Attributes -- #
    title = "New Invoice"
    
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        self.uid = EntryPopup.getText(self, title="User Select", message="Enter a UserID.")
        if not self.uid:
            App.app.openFrame("Start")
        
        user = self.client.user_get(userid=self.uid)
        if not user:
            messagebox.showerror("Invalid User ID", "No user exists with that User ID.")
            App.app.openFrame("Start")
        self.user = user[0]
        
        self.prints = self.client.print_get(paidby=self.uid, finished=True)
        self.added = []
        self.REF = "REF"
        self.NEW = "NEW"
        
        self.addWidgets()
        self.refresh()
    
    
    def addWidgets(self):
        rf = tk.Frame(self) # Right Pane
        lf = tk.Frame(self) # Left Pane
        
        self.vars = struct()
        self.vars.userid = "{}, {} ({})".format(self.user.lastname, self.user.firstname, self.uid)
        self.vars.numPrints = tk.IntVar(value=0)
        self.vars.cost = tk.StringVar(value="${:.2f}".format(0))
        
        ttk.Label(lf, text="User: ").grid(row=0, column=0, sticky="E")
        ttk.Label(lf, text=self.vars.userid).grid(row=0, column=1, sticky="W")
        ttk.Label(lf, text="# Prints: ").grid(row=1, column=0, sticky="E")
        ttk.Entry(lf, textvar=self.vars.numPrints, state="disabled").grid(row=1, column=1, sticky="W")
        ttk.Label(lf, text="Total:" ).grid(row=2, column=0, sticky="E")
        ttk.Entry(lf, textvar=self.vars.cost, state="disabled").grid(row=2, column=1, sticky="W")
        ttk.Button(lf, text="Create Invoice", command=self.addInvoice).grid(row=3, column=0, columnspan=2)
        ttk.Button(lf, text="Cancel", command=self.cancel).grid(row=4, column=0, columnspan=2)
        lf.pack(side="left", fill="y", expand="false")
        
        # Unadded Prints
        self.tablePrints = TableView(rf, columns=["Print ID", "Date", "Length", "Duration"])
        self.tablePrints.pack(side="top", fill="x", expand="true", padx=2, pady=2)
        f = tk.Frame(rf)
        ttk.Button(f, text="Add Prints to Invoice", command=self.add).pack(side="right", padx=2)
        ttk.Button(f, text="Remove Print", command=self.remove).pack(side="right")
        ttk.Button(f, text="Refund Print", command=self.addRefund).pack(side="right")
        f.pack(side="top", fill="x", expand="true")
        self.tableAdded = TableView(rf, columns=["Mode", "Print ID", "Date", "Cost"])
        self.tableAdded.pack(side="bottom", fill="x", expand="true", padx=2, pady=2)
        rf.pack(side="right", fill="both", expand="true")
        
        # Events
        self.tablePrints.bind("<Double-1>", lambda e: self.add)
        self.tableAdded.bind("<Double-1>", lambda e: self.remove)
        
        self.refresh()
    
    
    def add(self):
        prints = [row[0] for row in self.tablePrints.getRows()]
        [self.prints.remove(p) for p in prints]
        [self.added.append((self.NEW, p)) for p in prints]
        self.refresh()
    
    
    def addRefund(self):
        refunds = ListRefunds.getPrints(self, self.user)
        for refund in refunds:
            if refund.printid not in [t[1].printid for t in self.added]:
                self.added.append((self.REF, refund))
        self.refresh()
    
    
    def remove(self):
        tups = [row[0] for row in self.tableAdded.getRows()]
        for t in tups:
            self.added.remove(t)
            mode, p = t
            if mode == self.NEW:
                self.prints.append(p)
        self.refresh()
    
    
    def refresh(self):
        for t in self.added:
            if t[1] in self.prints:
                self.prints.remove(t[1])
        self.tablePrints.empty()
        [self.tablePrints.addRow((p, p.printid, p.date, p.length, p.duration)) for p in self.prints]
        self.tableAdded.empty()
        total = 0
        for t in self.added:
            mode, p = t
            date = datetime.strftime(p.date, "%Y-%m-%d %H:%M")
            cost = p.calcCost()
            if mode == self.REF:
                cost *= -1
            total += cost
            cost = "${:.2f}".format(cost)
            self.tableAdded.addRow((t, mode, p.printid, date, cost))
        self.vars.cost.set(round(total, 2))
        self.vars.numPrints.set(len(self.added))
    
    
    def addInvoice(self):
        added = [t[1] for t in self.added if t[0] == self.NEW]
        refunds = [t[1] for t in self.added if t[0] == self.REF]
        self.client.invoice_add(self.uid, prints=added, refunds=refunds)
        messagebox.showinfo("Invoice Created", "The invoice has been successfully created.")
    
    
    def cancel(self):
        App.app.openFrame("Start")



###################################################################################################
# ListRefunds                                                                         ListRefunds #
class ListRefunds(tk.Toplevel):
    def __init__(self, parent, user, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.client = parent.client
        self.parent = parent
        self.user = user
        
        # Set up filtering
        self.filter = struct()
        self.filter.invid = tk.StringVar()
        self.filter.printid = tk.StringVar()
        self.filter.dateMin = tk.StringVar()
        self.filter.dateMax = tk.StringVar()
        self.filter.costMin = tk.StringVar()
        self.filter.costMax = tk.StringVar()
        
        # Add Widgets
        self.addWidgets()
        self.filt()
        
        # Store selected prints for export
        self.selection = []
    
    
    def filt(self):
        # get list of all invoices
        invoices = self.client.invoice_get(userid=self.user.userid)
        
        # Make sure any filter entries are filled out correctly
        if not self.validate():
            return
        
        # Load filter entry data
        invid = self.filter.invid.get()
        printid = self.filter.printid.get()
        dateMin = self.filter.dateMin.get()
        dateMax = self.filter.dateMax.get()
        costMin = self.filter.costMin.get()
        costMax = self.filter.costMax.get()
        
        # Check invoices/prints
        self.prints = []
        for i in invoices:
            if invid and i.invid != int(invid):
                continue
            for p in i.prints:
                if printid and p.printid != printid:
                    continue
                if dateMin and p.date < datefstr(dateMin):
                    continue
                if dateMax and p.date > datefstr(dateMax):
                    continue
                if costMin and p.calcCost() < float(costMin):
                    continue
                if costMax and p.calcCost() > float(costMax):
                    continue
            self.prints.append(p)
        
        # Add prints to table
        self.table.empty()
        for p in self.prints:
            self.table.addRow((p, p.printid, "${:.2f}".format(p.calcCost())))
    
    
    def addWidgets(self):
        # Add Buttons Frame
        f1 = tk.Frame(self)
        ttk.Button(f1, text="Refund Prints", command=self.submit).pack(fill="x", side="top")
        ttk.Button(f1, text="Cancel", command=self.cancel).pack(fill="x", side="top")
        ttk.Button(f1, text="Filter", command=self.filt).pack(fill="x", side="bottom")
        f1.pack(side="right", fill="y")
        
        # Add Table
        self.table = TableView(self, columns=("Print ID", "Cost"))
        self.table.pack(side="top", fill="both")
        
        # Add Filter Form
        f = self.filter
        f2 = ttk.Labelframe(self, text="Filter")
        ttk.Label(f2, text="Invoice ID:").grid(row=0, column=0, sticky="E")
        ttk.Entry(f2, textvar=f.invid).grid(row=0, column=1, sticky="EW")
        ttk.Label(f2, text="Print ID:").grid(row=1, column=0, sticky="E")
        ttk.Entry(f2, textvar=f.printid).grid(row=1, column=1, sticky="EW")
        
        ttk.Label(f2, text="Min. Date:").grid(row=0, column=2, sticky="E")
        ttk.Entry(f2, textvar=f.dateMin).grid(row=0, column=3, sticky="EW")
        ttk.Label(f2, text="Max. Date:").grid(row=1, column=2, sticky="E")
        ttk.Entry(f2, textvar=f.dateMax).grid(row=1, column=3, sticky="EW")
        
        ttk.Label(f2, text="Min. Cost:").grid(row=0, column=4, sticky="E")
        ttk.Entry(f2, textvar=f.costMin).grid(row=0, column=5, sticky="EW")
        ttk.Label(f2, text="Max. Cost:").grid(row=1, column=4, sticky="E")
        ttk.Entry(f2, textvar=f.costMax).grid(row=1, column=5, sticky="EW")
        
        f2.rowconfigure((0,1), pad=2)
        f2.columnconfigure((0,1,2,3,4,5), pad=2)
        f2.pack(side="bottom", fill="x", ipadx=2, ipady=2, padx=2, pady=2)
    
    
    def validate(self):
        f = self.filter
        errmsg = []
        if f.invid.get() and not isint(f.invid.get()):
            errmsg.append("Invoice ID must be an integer.")
        if f.dateMin.get() and not isdate(f.dateMin.get()):
            errmsg.append("Min. Date is not a valid format.")
        if f.dateMax.get() and not isdate(f.dateMax.get()):
            errmsg.append("MAx. Date is not a valid format.")
        if f.costMin.get() and not isfloat(f.costMin.get()):
            errmsg.append("Min. cost must be a float.")
        if f.costMax.get() and not isfloat(f.costMax.get()):
            errmsg.append("Max. cost must be a float.")
        
        if errmsg:
            msg = "There are errors in your filter input.\n\n" + "\n".join(errmsg)
            messagebox.showerror("Validation Error", msg)
            return False
        else:
            return True
    
    
    def cancel(self):
        self.destroy()
    
    
    def submit(self):
        for row in self.table.getRows():
            self.selection.append(row[0])
        self.destroy()
    
    
    def getPrints(parent, user):
        win = ListRefunds(parent, user)
        selection = win.selection
        win.grab_set()
        parent.wait_window(win)
        return selection


###################################################################################################
# LogPaymentPage                                                                   LogPaymentPage #
class LogPaymentPage(Page):
    # -- Class Attributes -- #
    title = "Log Payment"
    
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        auth_userid, auth_passwd = UserVerify.getLogin(self)
        if not self.client.user_get(userid=auth_userid):
            messagebox.showerror("Authentication Error", "No login exists under that username.")
            return
        if not self.client.user_verify(auth_userid, auth_passwd):
            messagebox.showerror("Autherntication Error", "The username/password is invalid.")
            return
        if not self.client.user_issuper(auth_userid, auth_passwd):
            messagebox.showerror("Authentication Error", "You do not have permission to access this page.")
            return
            
        self.auth_userid = auth_userid
        self.auth_passwd = auth_passwd
        
        self.vars = struct() # Container for tk input variables
        self.addWidgets()
    
    
    def addWidgets(self):
        v = self.vars
        v.userid = tk.StringVar()
        v.payment = tk.StringVar()
        
        f = tk.Frame(self)
        ttk.Label(f, text="User ID (of user making payment):").grid(row=0, column=0, sticky="E")
        ttk.Entry(f, textvar=v.userid).grid(row=0, column=1, sticky="EW")
        ttk.Label(f, text="Payment Amount ($):").grid(row=1, column=0, sticky="E")
        ttk.Entry(f, textvar=v.payment).grid(row=1, column=1, sticky="E")
        f1 = tk.Frame(f)
        ttk.Button(f1, text="Submit", command=self.submit).pack(side="right", padx=2)
        ttk.Button(f1, text="Cancel", command=self.cancel).pack(side="right", padx=2)
        f1.grid(row=2, column=0, columnspan=2, sticky="E")
        f.columnconfigure((0,1), weight=1, pad=2)
        f.rowconfigure((0,1,2), weight=1, pad=2)
        f.pack()
        
    
    def submit(self):
        # Validate
        userid = self.vars.userid.get()
        payment = self.vars.payment.get()
        
        errmsg = []
        
        userids = self.client.user_get(userid=userid)
        if not userid:
            errmsg.append("No userid was provided.")
        elif not userids or userid not in [u.userid for u in userids]:
            errmsg.append("No user exists with that ID.")
        if not payment:
            errmsg.append("No payment amount was provided.")
        elif not isfloat(payment):
            errmsg.payment("Payment amount specified is not a number.")
        payment = float(payment)
        
        if errmsg:
            errmsg = "\n".join(errmsg)
            messagebox.showerror("Error", "Unable to log payment:\n\n" + errmsg)
            return
        
        u = [user for user in userids if user.userid == userid][0]
        s1, s2, s3 = u.firstname, u.lastname, payment
        msg = "You are registering a payment by {} {} for ${:.2f}. Is this correct?".format(s1, s2, s3)
        if messagebox.askyesno("Confirm", msg):
            self.client.payment_log(userid, payment, self.auth_userid, self.auth_passwd)
        
        # Reset fields
        self.vars.userid.set("")
        self.vars.payment.set("")
    
    
    def cancel(self):
        App.app.openFrame("Start")
        
        
###################################################################################################
# ViewOwingPage                                                                     ViewOwingPage #
class ViewOwingPage(Page):
    # -- Class Attributes -- #
    title = "View Amounts Owing"
    
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        # Ensure user has proper permisissions
        if not self.validate():
            return
        
        self.vars = struct()
        self.addWidgets()
    
    
    def addWidgets(self):
        ttk.Label(self, text=("Listed below are the account balances for each user. " + 
                              "Double-click on a row to view payment history.")).pack(side="top", fill="x")
        self.table = TableView(self, columns=("User ID", "Balance", "Type"), selectmode="browse")
        self.table.pack(side="bottom", fill="x", expand="true", padx=2, pady=2)
        self.table.bind("<Double-1>", self.ev_double1)
        self.refresh()
    
    
    def refresh(self):
        users = self.client.user_get()
        for u in users:
            balance = self.client.user_getowing(u.userid)
            type = "OWING"
            if balance < 0:
                balance *= -1
                type = "CREDIT"
            self.table.addRow((u, u.userid, "${:.2f}".format(balance), type))
    
    
    """ Querries user password and returns true if user has permission to view the page; false 
    otherwise. """
    def validate(self):
        auth_userid, auth_passwd = UserVerify.getLogin(self)
        if not self.client.user_get(userid=auth_userid):
            messagebox.showerror("Authentication Error", "No login exists under that username.")
            return False
        if not self.client.user_verify(auth_userid, auth_passwd):
            messagebox.showerror("Autherntication Error", "The username/password is invalid.")
            return False
        if not self.client.user_issuper(auth_userid, auth_passwd):
            messagebox.showerror("Authentication Error", "You do not have permission to access this page.")
            return False
        return True
        
        self.userid , self.passwd = auth_userid, auth_passwd
    
    
    """ The code to be run in the event the user double-clicks on a table row. """
    def ev_double1(self, event):
        user = self.table.getRows()[0]
        messagebox.showinfo("", "Support for viewing payment history has not yet been added.")
        