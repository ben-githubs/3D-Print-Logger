# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:36:25 2020

@author: Ben
"""

###################################################################################################
# IMPORTS                                                                                 IMPORTS #
# -- System Modules -- #
import tkinter as tk
from tkinter import messagebox, ttk

# -- Third Party -- #
import natsort as ns

# -- Custom -- #
from benutil import struct, isfloat
from gui_framework import Page, UserVerify, EntryPopup

###################################################################################################
# ListPrinterPage                                                                 ListPrinterPage #
class ListPrinterPage(Page):
    title = "Printers"
    
    # --------------------------------------------------------- ListPrinterPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
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
        sorted = [item for item in ns.natsorted(items, key=f)]
        
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
# ListRatePage                                                                       ListRatePage #
class ListRatePage(Page):
    # ------------------------------------------------------------ ListRatePage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
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
        sorted = [item for item in ns.natsorted(items, key=f)]
        
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
class AddRatePage(Page):
    # ------------------------------------------------------------- AddRatePage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
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
        if not self.verify():
            return
        else:
            auth_userid, auth_passwd = UserVerify.getLogin(self)
            if self.client.user_issuper(auth_userid, auth_passwd):
                try:
                    self.client.rate_add(v.rateid.get(), float(v.lengthrate.get()), 
                                         float(v.timerate.get()), v.name.get(), auth_userid, 
                                         auth_passwd)
                    self.parent.openFrame("ListRates")
                except Exception as e:
                    messagebox.showerror("Error", "An error occured while creating the rate:\n\n" + str(e))
            else:
                messagebox.showerror("Login Error", "Invalid login.")
    
    
    # ------------------------------------------------------------- AddRatePage -------- verify() #
    def verify(self):
            problems = []
            v = self.vars
            
            if not v.name.get():
                problems.append("You must enter a name.")
            elif self.client.rate_get(name=v.name.get()):
                problems.append("A rate with that name already exists.")
            if not v.rateid.get():
                problems.append("You must enter a rate ID.")
            elif self.client.rate_get(rateid=v.rateid.get()):
                problems.append("A rate with that ID already exists.")
            if not v.lengthrate.get():
                problems.append("You must enter a $ ammount per meter.")
            elif not isfloat(v.lengthrate.get()):
                problems.append("The $ ammount per m is not numerical.")
            elif float(v.lengthrate.get()) < 0:
                problems.append("The $ ammount per m must be greater than 0.")
            if not v.timerate.get():
                problems.append("You must enter a $ ammount per hr.")
            elif not isfloat(v.timerate.get()):
                problems.append("The $ ammount per hr is not numerical.")
            elif float(v.timerate.get()) < 0:
                problems.append("The $ ammount per hr must be greater than 0.")
            
            if not problems:
                return True
            else:
                msg = "The follwing errors were found in your input:\n\n"
                for s in problems:
                    msg += s + "\n"
                messagebox.showerror("Bad Input", msg)
                return False