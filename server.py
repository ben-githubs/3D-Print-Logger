# stuff
"""
Copyright Ben Airey, 2020

Free to use and edit.
"""

###################################################################################################
# Imports                                                                                 Imports #
# -- System Modules -- #
from configparser import ConfigParser
from datetime import date, datetime
import json
import logging
import pickle
import os
import re
import socket
import threading

# -- Custom Modules -- #
from commands import commands
from makerspace import PrintJob, Invoice, User, ServerRequest, ServerResponse, PrintRate


###################################################################################################
# Global Parameters                                                             Global Paremeters #
printers = {"Printer 1", "Printer 2", "Printer 3"}


###################################################################################################
# Server Class                                                                       Server Class #
class Server:
    def __init__(self, configPath):
        # Logging
        self.logger = logging.getLogger("app.server.Server")
        self.logger.propogate = False
        if not self.logger.handlers:
            f = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(f)
            self.logger.addHandler(ch)
        self.logger.info("Creating 'Server' instance.")
        
        # Instantiate kill switch
        self._kill = False
        
        
        # -- Load Configuration -----
        self.logger.debug("__init__: Loading server configuration...")
        conf = ConfigParser()
        conf.read(configPath)
        self.host = conf["MAIN"]["host"]
        self.port = conf["MAIN"].getint("port")
        self.DATA_PRINTS = conf["DATA"]["path_to_prints"]
        self.DATA_USERS = conf["DATA"]["path_to_users"]
        self.DATA_RATES = conf["DATA"]["path_to_rates"]
        self.DATA_PRINTERS = conf["DATA"]["path_to_printers"]
        self.DATA_INV = conf["DATA"]["path_to_invoices"]
        self.logger.debug("__init__: Finished loading configuation.")
        
        # Load command codes from text file
        self.logger.debug("__init__: Loading command codes...")
        self.com = commands()
        self.linkCommands()
        self.logger.debug("__init__: Finised loading codes.")
        
        
        # -- Import Locally Saved Data -----
        self.logger.debug("__init__: Searching for local data...")
        
        # Users
        self.users = set()
        if os.path.exists(self.DATA_USERS):
            self.logger.debug("__init__: Found local user data. Importing...")
            with open(self.DATA_USERS, "r") as f:
                data = json.loads(f.read())
                for d in data:
                    self.users.add(User.fromDict(d))
            self.logger.debug("__init__: Import finised.")
        else:
            self.logger.debug("__init__: No local user data.")
            self.users.add(User("admin", open("passwd.txt").read(), "n/a", issuper=True))
        
        # Print Jobs
        self.printjobs = list()
        if os.path.exists(self.DATA_PRINTS):
            self.logger.debug("__init__: Found local print data. Importing...")
            with open(self.DATA_PRINTS, "r") as f:
                data = json.loads(f.read())
                for d in data:
                    self.printjobs.append(PrintJob.fromDict(d))
            self.logger.debug("__init__: Import finished.")
        else:
            self.logger.debug("__init__: No local print data.")
        
        # Print Rates
        self.rates = set()
        if os.path.exists(self.DATA_RATES):
            self.logger.debug("__init__: Found local print rate data. Importing...")
            with open(self.DATA_RATES, "r") as f:
                data = json.loads(f.read())
                for d in data:
                    self.rates.add(PrintRate.fromDict(d))
            self.logger.debug("__init__: Import finised.")
        else:
            self.logger.debug("__init__: No local print rate data.")
        
        # Printers
        self.printers = set()
        if os.path.exists(self.DATA_PRINTERS):
            self.logger.debug("__init__: Found local printer data. Importing...")
            with open(self.DATA_PRINTERS, "r") as f:
                data = json.loads(f.read())
                for d in data:
                    self.printers.add(d)
            self.logger.debug("__init__: Import finished.")
        else:
            self.logger.debug("__init__: No local printer data found.")
        
        # Start Listener Thread
        self.logger.debug("__init__: Starting listener thread...")
        self.listenThread = threading.Thread(target=self.listen, args=(self.port,))
        self.listenThread.start()
        self.logger.debug("__init__: Finished thread start.")
        
        self.logger.info("Finished creating Server instance.")
        
    
    # ------------------------------------------------------------------------------- mainloop () #
    """ The main loop of the server, this should be called when the user expects to interact with
    the server through the console. It maintains a prompt for user input, and executes commands.
    """
    def mainloop(self):
        while not self._kill:
            cmd = input("server >> ")
            
            if cmd == "quit":
                self._kill = True
                self.listenThread.join()
    
    
    # --------------------------------------------------------------------------------- listen () #
    """ An asynchronous loop of the server, which listens for incoming connections and then assigns
    each its own thread for processing.
    
    Parameters:
        port: the port to listen on
    """
    def listen(self, port):
        self.logger.info("Opening socket...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                self.logger.info("Socket opened.")
                s.listen()
            except:
                self.logger.error("Couldn't open listening socket.")
                self.logger.info("Closing socket.")
                s.close()
            else:
                s.settimeout(0.2)
                while not self._kill:
                    try:
                        con, addr = con, addr = s.accept()
                    except socket.timeout:
                        pass
                    except:
                        raise
                    else:
                        self.logger.info("New connection!")
                        t = threading.Thread(target=self.onNewClient, args=(con, addr))
                        t.start()
                self.logger.info("Closing socket.")
                s.close()
    
    
    # ----------------------------------------------------------------------------- onNewClient() #
    """ This function will be called when a new client connects. """
    def onNewClient(self, con, addr):
        self.logger.debug("onNewClient: Connected with {}".format(addr))
        con.settimeout(0.2)
        while not self._kill:
            try:
                s_resp = self.parseCommand(con.recv(1024).decode("utf-8"))
                resp = s_resp.encode()
                con.sendall(resp)
            except socket.timeout:
                pass
            except ConnectionAbortedError:
                pass
    
    
    # ---------------------------------------------------------------------------- linkCommands() #
    """ Use this to control which functions link to the command codes. """
    def linkCommands(self):
        cmd = commands()
        self.fcns = {
                cmd.print.add : self.print_add,
                cmd.print.edit : self.print_edit,
                cmd.print.delete : self.print_delete,
                cmd.print.get : self.print_get,
                cmd.print.add_failed : self.print_addFailed,
                cmd.print.delete_failed : self.print_deleteFailed,
    
                cmd.user.add : self.user_add,
                cmd.user.edit : self.user_edit,
                cmd.user.delete : self.user_delete,
                cmd.user.verify : self.user_verify,
                cmd.user.get : self.user_get,
                cmd.user.issuper : self.user_issuper,
                
                cmd.rate.add : self.rate_add,
                cmd.rate.delete : self.rate_delete,
                cmd.rate.get : self.rate_get,
                
                cmd.printer.add : self.printer_add,
                cmd.printer.delete : self.printer_delete,
                cmd.printer.get : self.printer_get,
                }
    
    
    # ---------------------------------------------------------------------------- parseCommand() #
    """ Passed the raw json code send over the network, determines which functions to run and 
    passes their arguments. Returns 0 upon success, 1 upon syntax error, and 2 upon execution
    error.
    """
    def parseCommand(self, code):
        # Check Input
        if not code:
            return ServerResponse()
        
        # Check syntax
        try:
            self.logger.debug("parseCommand: Reading command...")
            s = ServerRequest.decode(code)
            if s.cmd not in self.fcns.keys():
                raise Exception("An unknown command code ({}) was passed.".format(s.cmd))
        except Exception as e:
            self.logger.exception("parseCommand: An exception was raised.")
            return ServerResponse(err=True, errmsg=str(e))
        self.logger.debug("parseCommands: Parsing complete. Attempting to execute...")
        
        # Execute commands
        try:
            v = self.fcns[s.cmd](*s.args, **s.kwargs)
            self.logger.debug("parseCommands: Done.")
            return ServerResponse(val=v)
        except Exception as e:
            self.logger.exception("parseCommand: Unable to execute command.")
            return ServerResponse(err=True, errmsg=str(e))# Return excecution error
    
    
    # -----------------------------------------------------------------------------  savePrints() #
    """ Save all the print jobs to the disk. """
    def savePrints(self):
        self.logger.debug("savePrints: Saving user data...")
        try:
            with open(self.DATA_PRINTS, "w+") as f:
                # We make a list of dictionary-representations of every print on the server, then
                # easily convert the list to json format, which we then write to a file.
                f.write(json.dumps([p.dict() for p in self.printjobs]))
            self.logger.debug("savePrints: Save completed.")
        except:
            self.logger.exception("savePrints: Unable to save data!")
    
    
    # ------------------------------------------------------------------------------  saveUsers() #
    """ Save all the user information to the disk. """
    def saveUsers(self):
        self.logger.debug("saveUsers: Saving user data...")
        try:
            with open(self.DATA_USERS, "w+") as f:
                # We make a list of dictionary-representations of every user on the server, then
                # easily convert the list to json format, which we then write to a file.
                f.write(json.dumps([u.dict() for u in self.users]))
            self.logger.debug("saveUsers: Save completed.")
        except:
            self.logger.exception("saveUsers: Unable to save data!")
    
    
    # ------------------------------------------------------------------------------  saveRates() #
    """ Save all the print rate information to the disk. """
    def saveRates(self):
        self.logger.debug("saveRates: Saving print rate data...")
        try:
            with open(self.DATA_RATES, "w+") as f:
                f.write(json.dumps([r.dict() for r in self.rates]))
            self.logger.debug("saveRates: Save completed.")
        except:
            self.logger.exception("saveRates: Unable to save data!")
    
    
    # ---------------------------------------------------------------------------  savePrinters() #
    """ Save all the printer information to the disk. """
    def savePrinters(self):
        self.logger.debug("savePrinters: Saving printer data...")
        try:
            with open(self.DATA_PRINTERS, "w+") as f:
                f.write(json.dumps(list(self.printers)))
            self.logger.debug("savePrinters: Save completed.")
        except:
            self.logger.exception("savePrinters: Unable to save data!")
    
    
    # ---------------------------------------------------------------------------  saveInvoices() #
    """ Save all the invoices to the disk. """
    def saveInvoices(self):
        pickle.dump(Invoice.invoices, self.DATA_INV)
    
    
    # ---------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------- PRINT LOGGING FUNCTIONS #
    
    # ------------------------------------------------------------------------------  print_add() #
    """ Creates a new PrintJob object and stores it locally. Returns a reference to the object.
    Parameters:
        code: A string, formatted as json code, which is used to create a PrintJob object.
    """
    def print_add(self, userid, passwd, length, duration, rate, printer, paidby="", note=""):
        self.logger.info("print_add: Logging new print...")
        self.logger.debug("print_add: Verifying user...")
        assert self.user_verify(userid, passwd), "Invalid username or password."
        self.logger.debug("print_add: User verified.")
        self.logger.debug("print_add: Creating PrintJob object...")
        printid = self.print_genID(datetime.now(), printer, rate)
        printjob = PrintJob(userid, printer, length, duration, rate, printid=printid, note=note, 
                            paidBy=paidby)
        self.printjobs.append(printjob)
        self.logger.debug("print_add: Finished creating object.")
        self.logger.debug("print_add: Saving to disk...")
        self.savePrints()
        self.logger.debug("print_add: Saved.")
        self.logger.info("print_add: Finsihed logging new print.")
        return printjob
    
    
    # ------------------------------------------------------------------------------ print_edit() #
    def print_edit(self, *args, **kwargs):
        pass
    
    
    # ---------------------------------------------------------------------------- print_delete() #
    def print_delete(self, *args, **kwargs):
        pass
    
    
    # ------------------------------------------------------------------------------- print_get() #
    def print_get(self, userid="", printid="", paidby="", lengthMin=None, lengthMax=None,
                  durationMin=None, durationMax=None, dateMin=None, dateMax=None, finished=None,
                  rate=None):
        matches = list()
        
        self.logger.debug("print_get: Here is a list of ALL prints: {}".format([p.printid for p in self.printjobs]))
        
        for p in self.printjobs:
            if printid and not re.match(printid, p.printid):
                continue
            if userid and not re.match(userid, p.userid):
                continue
            if paidby and not re.match(paidby, p.paidBy):
                continue
            if type(lengthMin) in {int, float} and p.length < lengthMin:
                continue
            if type(lengthMax) in {int, float} and p.length > lengthMax:
                continue
            if durationMin in {int, float} and p.duration < durationMin:
                continue
            if durationMax in {int, float} and p.duration > durationMax:
                continue
            if dateMin and p.date < dateMin:
                continue
            if dateMax and p.date > dateMax:
                continue
            if finished != None and finished != p.finished:
                continue
            if rate != None and p.rate.rateid != rate.rateid:
                continue
            
            matches.append(p)
        
        self.logger.debug("print_get: Here's the filtered list: {}".format([p.printid for p in matches]))
        
        return matches
                
    
    
    # ------------------------------------------------------------------------- print_addFailed() #
    def print_addFailed(self, printid, length, duration):
        # Make sure printid exists
        assert printid in [p.printid for p in self.printjobs]
        
        # Get corresponding print object
        printjob = None
        for p in self.printjobs:
            if p.printid == printid:
                printjob = p
                break
        
        # Add Failed Print
        printjob.addFailed(length, duration)
        self.savePrints()
        return True
    
    
    # ---------------------------------------------------------------------- print_deleteFailed() #
    def print_deleteFailed(self, *args, **kwargs):
        pass
    
    
    # ----------------------------------------------------------------------------- print_genID() #
    """ Generates a print id based on the provided information. """
    def print_genID(self, d, printer, rate):
        n = 1
        print(self.printjobs)
        for printjob in self.printjobs:
            if printjob.date.date() == d.date() and printjob.printer == printer:
                n += 1
        
        return "{0}-{1}-{2} {3:03d}".format(d.strftime("%d%m%y"), printer, rate.rateid, n)
    
    
    # ---------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------- PRINT RATES #
    
    # -------------------------------------------------------------------------------- rate_add() #
    """ Returns all print rates. """
    def rate_add(self, rateid="", lengthrate=0, timerate=0, name="", auth_userid="", auth_passwd=""):
        if self.user_issuper(auth_userid, auth_passwd):
            assert rateid not in [r.rateid for r in self.rates], "Print Rate ID '{}' is already taken.".format(rateid)
            self.logger.debug("rate_add: Arguments")
            [self.logger.debug("    {}".format(a)) for a in [rateid, lengthrate, timerate, name, auth_userid, auth_passwd]]
            rate = PrintRate(rateid, lengthrate, timerate, name=name)
            self.rates.add(rate)
            self.logger.debug("rate_add: The following rate was created:\n{}".format(str(rate.dict())))
            self.saveRates()
        else:
            raise Exception("You are not authorized to create a new rate.")
    
    
    # ----------------------------------------------------------------------------- rate_delete() #
    """ Deletes all rates whose rate ID's appear in the list 'rateids'. """
    def rate_delete(self, rateids):
        assert type(rateids) == list
        for r in rateids:
            assert type(rateids) == str
        
        for r in self.rates:
            if r.rateid in rateids:
                self.rates.remove(r)
        
        self.saveRates()
        return
    
    
    # -------------------------------------------------------------------------------- rate_get() #
    """ Given the criteria, returns a set of all matching PrintRate objects. """
    def rate_get(self, rateid="", name="", lengthMin=None, lengthMax=None, timeMin=None,
                 timeMax=None):
        matches = set()
        
        self.logger.debug("rate_get: Here is a list of ALL rates: {}".format([r.rateid for r in self.rates]))
        
        for r in self.rates:
            if rateid and not re.match(rateid, r.rateid):
                continue
            if name and not re.match(name, r.name):
                continue
            if type(lengthMin) in {int, float} and r.lengtheate < lengthMin:
                continue
            if type(lengthMax) in {int, float} and r.lengthrate > lengthMax:
                continue
            if type(timeMin) in {int, float} and r.timeRate < timeMin:
                continue
            if type(timeMax) in {int, float} and r.timerate > timeMax:
                continue
            
            matches.add(r)
        
        self.logger.debug("rate_get: Here's the filtered list: {}".format([r.rateid for r in matches]))
        
        return list(matches)
    
    
    # ---------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------- PRINTER #
    
    # ----------------------------------------------------------------------------  printer_add() #
    """ Adds a new printer. """
    def printer_add(self, printer, auth_userid, auth_passwd):
        if not self.user_issuper(auth_userid, auth_passwd):
            raise Exception("This user ({}) is not allowed to add a printer.".format(auth_userid))
        if printer in self.printers:
            raise Exception("There is already a printer called '{}'.".format(printer))
        self.printers.add(printer)
        self.savePrinters()
    
    
    # -------------------------------------------------------------------------  printer_delete() #
    """ Remove a printer. """
    def printer_delete(self, printer, auth_userid, auth_passwd):
        if not User.issuper(auth_userid, auth_passwd):
            raise Exception("This user ({}) is not allowed to remove a printer.".format(auth_userid))
        if printer not in self.printers:
            raise Exception("There is not a printer called '{}'.".format(printer))
        self.printers.remove(printer)
        self.savePrinters()
    
    
    # ----------------------------------------------------------------------------- printer_get() #
    """ Returns a set of printers who's names match the regex pattern given. """
    def printer_get(self, pat=".*"):
        matches = set()
        for p in self.printers:
            if re.match(pat, p):
                matches.add(p)
        
        return list(matches)
    
    
    # ---------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------- USER MANAGEMENT #
    
    # -------------------------------------------------------------------------------  user_add() #
    """ Adds a new user to the program.
    Parameters:
        userid: a unique ID for the user
        passwd: a passphrase the user can use for verification
        issuper: a boolean flag designating whether or not the account has special privaledges.
    """
    def user_add(self, userid, passwd, email, issuper=False, auth_userid="", auth_passwd="", 
                firstname="", lastname=""):
        assert type(userid) == str
        assert type(passwd) == str
        assert type(email) == str
        assert type(issuper) == bool
        assert type(auth_userid) == str
        assert type(auth_passwd) == str
        assert type(firstname) == str
        assert type(lastname) == str
        
        # Make sure that if we're making a privaleged user, that we have the approval of an 
        # authorized user
        if issuper and not self.user_issuper(auth_userid, auth_passwd):
            raise Exception("Authorization for elevated user was invalid. Either the user information is wrong, or the user is not authorized to create elevated accounts.")
        
        self.logger.info("user_add: Adding new user, {}, to the userlist.".format(userid))
        u = User(userid, passwd, email, issuper=issuper, lastname=lastname, firstname=firstname)
        self.users.add(u)
        self.logger.debug("user_add: Saving userlist changes to disk.")
        self.saveUsers()


    # ----------------------------------------------------------------------------- user_verify() #
    """ Checks if a user's credentials are valid. """
    def user_verify(self, userid, passwd):
        assert type(userid) == str
        assert type(passwd) == str
        
        u = self.user_get(userid)
        if u and u[0].passwd == passwd:
            return True
        else:
            return False
    
    
    # ---------------------------------------------------------------------------- user_issuper() #
    """ Checks if a user is a superuser. """
    def user_issuper(self, userid, passwd):
        return self.user_verify(userid, passwd) and self.user_get(userid)[0].issuper
    
    # -------------------------------------------------------------------------------- user_get() #
    """ Returns a set of users which match the given criteria. 
    Parameters:
        userid: (optional) [str] a regex pattern. If given, only users whose ID matches the pattern
                will be returned.
        issuper: (optional) [bool] whether or not the user is a super user. If given, only users
                 who match this value (True or False) will be returned.
        email: (optional) [str] a regex pattern. If given, only users whose email matches the 
               pattern will be returned.
        firstname: (optional) [str] a regex pattern. If given, only users whose email matches the 
                   pattern will be returned.
        lastname: (optional) [str] a regex pattern. If given, only users whose email matches the 
                  pattern will be returned.
    """
    def user_get(self, userid="", issuper=None, lastname="", firstname="", email=""):
        # -- Check Parameter Types -----
        assert type(userid) == str
        assert type(email) == str
        assert type(firstname) == str
        assert type(lastname) == str
        assert type(issuper) in {bool, type(None)}
        
        # -- Filtering -----
        matches = set()
        # Loop through every user, and if it meets all the requirements, add it to 'matches'.
        for user in self.users:
            # For these checks, we use regex to check the current userid to the patterns we've been
            # given. 
            if userid:
                if not re.match(userid, user.userid):
                    continue            
            if email:
                if not re.match(email, user.email):
                    continue            
            if firstname:
                if not re.match(firstname, user.firstname):
                    continue
            if lastname:
                if not re.match(lastname, user.lastname):
                    continue
            
            # Here, we just check if issuper is the same value as specified.
            if type(issuper) != type(None):
                if user.issuper != issuper:
                    continue
            
            matches.add(user) # If we failed any of the earleir tests, we wouldn't be here.
        
        return list(matches)
    
    
    # ------------------------------------------------------------------------------- user_edit() #
    """ Edits the information profile of a user. """
    def user_edit(self, userid, auth_userid, auth_passwd, passwd="", email="", firstname="",
                  lastname="", issuper="no"):
        # Make sure this is being authorized
        auth = 0 # Unprivaledged
        if self.user_issuper(auth_userid, auth_passwd):
            auth = 2 # Allowed to do whatever the fuck they want
        elif auth_userid == userid and self.user_verify(auth_userid, auth_passwd):
            auth = 1 # Allowed to change basic info, but nothing crazy
        
        assert auth, "User '{0}' does not have permission to edit '{1}'s profile.".format(auth_userid, auth_passwd)
        
        
        # Now, make the changes
        user = self.user_get(userid)[0]
        if passwd:
            user.passwd = passwd
        if email:
            user.email = email
        if firstname:
            user.firstname = firstname
        if lastname:
            user.lastname = lastname
        
        if auth == 2:
                user.issuper = issuper
        
        # Save changes
        self.saveUsers()
        return
    
    
    # ----------------------------------------------------------------------------- user_delete() #
    """ Deletes one or more users. """
    def user_delete(self, userids, auth_userid="", auth_passwd=""):
        # -- Check Input -----
        assert type(userids) == list
        for u in userids:
            assert type(u) == str
        assert type(auth_userid) == str
        assert type(auth_passwd) == str
        
        assert self.user_issuper(auth_userid, auth_passwd)
        
        # -- Find all Users whose userid matches the above -----
        for u in self.user_get(userid="(" + ")|(".join(userids) + ")"):
            self.users.remove(u)
        return

                
        
        



if __name__ == "__main__":
    print("Starting server...")
    s = Server()
    s.mainloop()
        