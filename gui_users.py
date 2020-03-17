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
from benutil import struct
from gui_framework import App, Page, UserVerify


###################################################################################################
# ListUserPage                                                                       ListUserPage #
class ListUserPage(Page):
    title = "Users"
    
    # ------------------------------------------------------------ ListUserPage ------ __init__() #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
        self.addWidgets()
        self.refreshTree()
    
    
    # ------------------------------------------------------------ ListUserPage ---- addWidgets() #
    def addWidgets(self):
        # Add Buttons
        f = tk.Frame(self)
        ttk.Button(f, text="Add User", width=20, command=lambda: App.app.openFrame("AddUser")).pack(side="top")
        ttk.Button(f, text="Edit User", width=20, command=self.edit).pack(side="top")
        ttk.Button(f, text="Delete User", width=20, command=self.delete).pack(side="top")
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
            users = self.client.user_get()
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
        sorted = [item for item in ns.natsorted(items, key=f)]
        
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
        
        self.logger.debug("edit: User is {}".format(who_id))
        
        # If the user is editing their own profile, then verify their credentials. Otherwise, make
        # sure the user is a mod before allowing them to edit the profile.
        
        verified = False
        try:
            verified = self.client.user_verify(who_id, who_pass)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        
        if not verified:
            messagebox.showerror("Bad Login", "Your login was incorrect. Are you sure you used the correct password?")
            return
        elevated = self.client.user_issuper(who_id, who_pass)
        if not who_id == userid and not elevated:
            messagebox.showerror("Access Denied", "You do not have permission to edit this user.")
        elif not self.client.user_get(userid):
            messagebox.showerror("Error", "Can't edit this user - apparently it doesn't exist.")
        else:
            auth = (who_id, who_pass)
            App.app.openFrame("EditUser", userid=userid, elevated=elevated, auth=auth)
    
    
    # ------------------------------------------------------------ ListUserPage -------- delete() #
    """ Removes a user. """
    def delete(self):
        messagebox.showinfo("Info", "This feature is not yet implemented.")


###################################################################################################
# AddUserPage                                                                         AddUserPage #
class AddUserPage(Page):
    title = "Add User"
    
    # ----------------------------------------------------------- AddUserPage ------- __init__ () #
    def __init__(self, parent, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        
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
        problems = []
        v = self.vars
        
        if not v.userid.get():
            problems.append("Please enter a User ID.")
        elif self.client.user_get(userid=v.userid.get()):
            problems.append("The User ID is already in use. Please choose another.")
        if not v.passwd1.get() or not v.passwd2.get():
            problems.append("Please enter the password twice.")
        elif v.passwd1.get() != v.passwd2.get():
            problems.append("The passwords so not match.")
        if v.issuper.get():
            if not v.auth_userid.get() or not v.auth_passwd.get():
                problems.append("To create an elevated user, please provide authorization from an existing elevated account.")
            elif not self.client.user_issuper(v.auth_userid.get(), v.auth_passwd.get()):
                problems.append("The authorization User ID and/or password was incorrect.")
        if not v.email.get():
            problems.append("Please provide an email address.")
        if not v.lastname.get():
            problems.append("Please enter a last name/organization name.")
            
        if not problems:
            return True
        else:
            msg = "The following errors were found in the supplied information.\n\n"
            for s in problems:
                msg += s + "\n"
            messagebox.showerror("Bad Input", msg)
            return False
    
    
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
        client = self.client
        
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
                    client.user_add(uid, pwd, issuper=sup, auth_userid=auid, auth_passwd=apwd, 
                                   email=eml, firstname=fnm, lastname=lnm)
                messagebox.showinfo("Info", "New user successfully created!")
                self.clearInput()
            except Exception as e:
                self.logger.exception("An error occured while verifying input.")
                messagebox.showerror("Error", "Something went wrong while adding the new user:\n\n{}".format(str(e)))


###################################################################################################
# EditUserPage                                                                       EditUserPage #
class EditUserPage(Page):
    title = "Edit User"
    
    # ------------------------------------------------------------ EditUserPage ----- __init__ () #
    def __init__(self, parent, userid, elevated=False, auth=("",""), *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        self.userid = userid
        self.elevated = elevated
        self.auth = auth # Holds the info of whoever is authorizing the changes
        
        self.addWidgets()
        self.loadUser(userid, elevated=elevated)
    
    
    # ------------------------------------------------------------ EditUserPage ------ loadUser() #
    def loadUser(self, userid, elevated=False):
        u = self.client.user_get(userid)[0]
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
        if self.vars.passwd1.get() or self.vars.passwd2.get():
            if self.vars.passwd1.get() != self.vars.passwd2.get():
                messagebox.error("Invalid", "Passwords do not match.")
        
        # Copy everything
        v = self.vars
        try:
            self.client.user_edit(v.userid.get(), self.auth[0], self.auth[1], 
                                        issuper=v.issuper.get(), email=v.email.get(), passwd=v.passwd1.get(),
                                        firstname=v.firstname.get(), lastname=v.lastname.get())
            messagebox.showinfo("Saved", "Changes successfully saved!")
            App.app.openFrame("ListUsers")
        except Exception as e:
            self.logger.exception("EditUserPage.save")
            messagebox.showerror("Error", str(e))