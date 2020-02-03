# stuff
"""
Copyright Ben Airey, 2020

Free to use and edit.
"""

###################################################################################################
# Imports                                                                                 Imports #
# -- System Imports -- #
from datetime import datetime
import json
import logging

# -- Custom Imports -- #
from benutil import trycatch


###################################################################################################
# Logging                                                                                 Logging #
format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
u_logger = logging.getLogger("app.makerspace.User")
res_logger = logging.getLogger("app.makerspave.ServerResponse")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(format)
if not len(u_logger.handlers):
    u_logger.addHandler(ch)
if not len(res_logger.handlers):
    res_logger.addHandler(ch)

###################################################################################################
# PrintJob Class                                                                   PrintJob Class #
""" A basic class to describe an individual print job. """
class PrintJob:
    
    # ---------------------------------------------------------------- PrintJob -----  __init__() #
    """ Initializer.
    Parameters:
        userid: the username of the person who startd this print job.
        printer: the id of the printer on ehich the job is being done.
        date: a datetime object of when the print job is processed. If not specified, 
              datetime.now() is used by default.
        printid: the job number used to specify this print. If left blank, one is generated using
                 the information supplied.
        length: the length of fillament used, in meters.
        duration: the integer number of minutes the job should take to complete.
        rateid: specifies the rate the print should be charged at (such as personal, research, 
                etc.)
        paidBy: the userid of the person who is responsible for paying for this
        approvedBy: the userid of the person who approved the print
    """
    def __init__(self, userid, printer, length, duration, rate, paidBy, approvedBy="", 
                 date=datetime.now(), printid="", note="", finished=False):
        # -- Check Input -- #
        assert type(userid) == str, "Expected 'str', got '{}'".format(type(userid))
        assert type(printer) == str, "Expected 'str', got '{}'".format(type(printer))
        assert type(length) == float, "Expected 'float', got '{}'".format(type(length))
        assert type(duration) in {int, float}, "Expected number, got '{}'".format(type(duration))
        assert type(rate) == PrintRate, "Expected 'PrintRate', got '{}'\n{}".format(type(rate), str(rate))
        assert type(paidBy) == str, "Expected 'str', got '{}'".format(type(paidBy))
        assert type(approvedBy) == str, "Expected 'str', got '{}'".format(type(approvedBy))
        assert type(date) == datetime, "Expected 'datetime', got '{}'".format(type(date))
        assert type(printid) == str, "Expected 'str', got '{}'".format(type(printid))
        assert type(note) == str, "Expected 'str', got '{}'".format(type(note))
        assert type(finished) == bool, "Expected 'bool', got '{}'".format(type(finished))
        
        self.rate = rate
        
        # Generate printid, if necessary
        if printid == "":
            printid = PrintJob.genPrintid(date, printer, self.rate)
        
        # Assign variables
        self.userid = userid
        self.printer = printer
        self.length = length
        self.duration = duration
        self.date = date
        self.printid = printid
        self.approvedBy = approvedBy
        self.paidBy = paidBy
        self.note = note
        
        # Initialize a list for failed print objects, so that we can keep track of those mistakes.
        self.failedPrints = list()
        
        # Have a flag for keeping track of which invoice this print is on
        self.invoice = ""
        
        # Have a flag for whether or not the print is finished
        self.finished = False
    
    
    # ---------------------------------------------------------------- PrintJob ---------- dict() #
    """ Returns a dictionary with the values of every attribute of this object. """
    def dict(self):
        d = dict()
        d["__class__"] = "PrintJob"
        d["userid"] = self.userid
        d["printer"] = self.printer
        d["length"] = self.length
        d["duration"] = self.duration
        d["rate"] = self.rate.dict()
        d["date"] = self.date.isoformat()
        d["printid"] = self.printid
        d["paidBy"] = self.paidBy
        d["note"] = self.note
        d["finished"] = self.finished
        d["failedPrints"] = [f.dict() for f in self.failedPrints]
        
        return d
    
    
    # ---------------------------------------------------------------- PrintJob ------ fromDict() #
    """ Returns a PrintJob objects whose attributes are taken from the values of a dictionary. """
    def fromDict(d):
        userid = d["userid"] # String
        printer = d["printer"] # String
        length = d["length"] # Float
        duration = d["duration"] # Int
        rate = d["rate"] # PrintRate or dict
        date = d["date"] # Datetime or string
        printid = d["printid"] # String
        paidBy = d["paidBy"] # String
        note = d["note"] # String
        finished = d["finished"] # Bool
        
        if type(rate) == dict:
            rate = PrintRate.fromDict(rate)
        if type(date) == str:
            date = datetime.fromisoformat(date)
        
        printjob = PrintJob(userid, printer, length, duration, rate, paidBy, date=date, 
                            printid=printid, note=note, finished=finished)
        
        for f in d["failedPrints"]:
            if type(f) == dict:
                f = PrintJob.FailedPrint.fromDict(f)
            printjob.failedPrints.append(f)
        
        return printjob
    
    
    # ---------------------------------------------------------------- PrintJob -------- decode() #
    """ Decodes a PrintJob object from a json string. """
    def decode(code):
        data = json.loads(code)
        return PrintRate.fromDict(data)
    
    
    # ---------------------------------------------------------------- PrintJob -------- encode() #
    """ Encodes the PrintJob object as a json string. """
    def encode(self):
        return json.dumps(self.dict())
    
    
    # ---------------------------------------------------------------- PrintJob ---- genPrintid() #
    """ Generates a print id based on the provided information. """
    def genPrintid(date, printer, rate):
        # Check Input
        assert type(date) == datetime, "Parameter 'date' must be a datetime object."
        assert type(printer) == str, "Parameter 'printer' must be a string."
        assert printer != "", "Parameter 'printer' cannot be an empty string."
        assert type(rate) == PrintRate, "Parameter 'rate' must be a PrintRate object."
        
        # Count how many jobs have been printed today on the same printer
        same = 1
        for printjob in PrintJob.printjobs:
            if printjob.date.date() == date.date() and printjob.printer == printer:
                same += 1
        
        return "{0}-{1}-{2} {3:03d}".format(date.strftime("%d%m%y"), printer, rate.rateid, same)
    
    
    # ---------------------------------------------------------------- PrintJob ----- addFailed() #
    def addFailed(self, length, duration):
        assert type(length) in {float, int}, "Parameter 'length' must be numeric."
        assert length > 0, "Parameter 'length' must be greater than zero. Recieved: {:f}".format(length)
        assert type(duration) == int, "Parameter 'duration' must be an integer. Recieved: {:.0f}".format(duration)
        assert duration > 0, "Parameter 'duration' must be greater than zero."
        
        # If this PrintJob is finished, then don't add anything
        assert not self.finished, "This print job is closed; cannot add failed print."
        
        self.failedPrints.append(PrintJob.FailedPrint(length, duration))
    
    
    # ---------------------------------------------------------------- PrintJob -----  calcCost() #
    """ Calculates the total cost associated with the print job. Returns in dollars."""
    def calcCost(self):
        cost = self.rate.calcCost(self.length, self.duration)
        for f in self.failedPrints:
            cost += self.rate.calcCost(f.length, f.duration)
        
        return cost
    
    
    # ---------------------------------------------------------------- PrintJob -------  __eq__() #
    """ Overrides the == operator for the class. My strategy here is that two prints are equal if
    if they contain the same information, and if they contain the same information, then their
    exported json strings should be identical. So that's what we comapre. """
    def __eq__(self, obj):
        return isinstance(obj, PrintJob) and obj.encode() == self.encode()
    
    # ------------------------------------------------------------------------------  FailedPrint #
    #                                                                                    SUBCLASS #
    """ A smaller class, which stores the basic information needed to track print failures. """
    class FailedPrint:
        def __init__(self, length, duration):
            assert type(length) in {float, int}, "Parameter 'length' must be numeric."
            assert length > 0, "Parameter 'length' must be greater than zero."
            assert type(duration) == int, "Parameter 'duration' must be an integer."
            assert duration > 0, "Parameter 'duration' must be greater than zero."
            
            self.length = length
            self.duration = duration
        
        
        # --------------------------------------------------------- FailedPrint ---------- dict() #
        """ Returns a dictionary containing the values of every attribute of this object. """
        def dict(self):
            d = dict()
            d["__class__"] = "FailedPrint"
            d["length"] = self.length
            d["duration"] = self.duration
            return d
        
        
        # --------------------------------------------------------- FailedPrint ------ fromDict() #
        """ Returns a FailedPrint objects whose attributes are taken from the values of a 
        dictionary. """
        def fromDict(d):
            return PrintJob.FailedPrint(d["length"], d["duration"])
    
    
        # --------------------------------------------------------- FailedPrint -------- decode() #
        """ Decodes a FailedPrint object from a json string. """
        def decode(code):
            data = json.loads(code)
            return PrintJob.FailedPrint.fromDict(data)
    
    
        # --------------------------------------------------------- FailedPrint -------- encode() #
        """ Encodes the FailedPrint object as a json string. """
        def encode(self):
            return json.dumps(self.dict())
            

###################################################################################################
# PrintRate Class                                                                 PrintRate Class #
""" A class to represent different printing rates for various purposes. """
class PrintRate:
    rates = set()
    
    
    # --------------------------------------------------------------- PrintRate -----  __init__() #
    def __init__(self, rateid, lengthrate, timerate, name=None):
        assert type(rateid) == str, "Parameter 'rateid' must be a string."
        assert type(lengthrate) == float, "Parameter 'lengthrate' must be a float."
        assert lengthrate >= 0, "Parameter 'lengthrate' cannot be negative."
        assert type(timerate) == float, "Parameter 'timerate' must be a float."
        assert timerate >= 0, "Parameter 'timerate' cannot be negative."
        
        if name == None:
            name = rateid
        
        self.rateid = rateid
        self.name = str(name)
        self.lengthrate = lengthrate
        self.timerate = timerate
    
    
    # --------------------------------------------------------------- PrintRate ---------- dict() #
    """ Returns a dictionary with the values of every attribute of this object. """
    def dict(self):
        d = dict()
        d["__class__"] = "PrintRate"
        d["rateid"] = self.rateid
        d["name"] = self.name
        d["lengthrate"] = self.lengthrate
        d["timerate"] = self.timerate
        return d
    
    # --------------------------------------------------------------- PrintRate ------ fromDict() #
    """ Returns a Printrate object whose attributes are taken from the values of a dictionary. """
    def fromDict(d):
        return PrintRate(d["rateid"], d["lengthrate"], d["timerate"])
    
    
    # --------------------------------------------------------------- PrintRate -------- decode() #
    """ Decodes a PrintRate object from a json string. """
    def decode(code):
        data = json.loads(code)
        return PrintRate.fromDict(data)
    
    
    # --------------------------------------------------------------- PrintRate -------- encode() #
    """ Encodes the PrintRate object as a json string. """
    def encode(self):
        return json.dumps(self.dict())
    
    
    # --------------------------------------------------------------- PrintRate -----  calcCost() #
    """ Calculates the total cost of a print job, using the supplied length and duration, and the
    cost per meter and hour for this PrintRate. """
    def calcCost(self, length, duration):
        assert type(length) == float, "Parameter 'length' must be a float."
        assert type(duration) == int, "Parameter 'duration' must be an integer."
        
        hours = duration / 60
        return length*self.lengthrate + hours*self.timerate


###################################################################################################
# Invoice Class                                                                     Invoice Class #
class Invoice:
    # ----------------------------------------------------------------- Invoice -----  __init__() #
    def __init__(self, userid, invid, date=datetime.now(), prints=set(), refunds=set()):
        assert type(userid) == str, "Expected 'str', got '{}'.".format(type(userid))
        assert type(invid) == int, "Expected 'int', got '{}'.".format(type(invid))
        assert type(date) == datetime, "Expected 'datetime', got '{}'.".format(type(date))
        assert type(prints) == set, "Expected 'set', got '{}'.".format(type(prints))
        for p in prints:
            assert type(print) == PrintJob, "Expected 'PrintJob', got '{}'.".format(type(p))
            assert p.paidBy == userid, "Cannot add a print which is paid by another person."
            assert p.finished, "Cannot add a print which is not finished."
        assert type(refunds) == set, "Expected 'set', got '{}'.".format(type(refunds))
        for p in refunds:
            assert type(refunds) == PrintJob, "Expected 'PrintJob', got '{}'.".format(type(p))
            assert p.paidBy == userid, "Cannot add a print which is paid by another person."
            assert p.finished, "Cannot add a print which is not finished."
        
        self.userid = userid
        self.invid = invid
        self.date = date
        self.prints = prints
    
    
    # ----------------------------------------------------------------- Invoice ------ calcCost() #
    def calcCost(self):
        return sum([p.calcCost() for p in self.prints]) - sum([p.calcCost() for p in self.refunds])
    
    
    # ----------------------------------------------------------------- Invoice ----- exportCSV() #
    def exportCSV(self):
        f = "Invoice No., {}\n".format(self.invid)
        f += "User ID, {}\n".format(self.userid)
        f += "Total Cost, ${:.2f}\n".format(self.calcCost())
        # Headings
        f += "Print ID, Printed By (User ID), Print Date, Print Length, Print Duration, Rate, Cost,\n"
        for p in self.refunds:
            r = p.rate.name
            c = p.rate.calcCost(p.length, p.duration)
            f += "{},{},{},{},{},{},{}\n".format(p.printid, p.userid, p.date.isoformat, p.length, p.duration, r, -c)
            for fp in p.failedPrints:
                c = p.rate.calcCost(fp.length, fp.duration)
                f += "Failed Print,,,{},{},{},{}\n".format(fp.length, fp.duration, r, -c)
        for p in self.prints:
            r = p.rate.name
            c = p.rate.calcCost(p.length, p.duration)
            f += "{},{},{},{},{},{},{}\n".format(p.printid, p.userid, p.date.isoformat, p.length, p.duration, r, c)
            for fp in p.failedPrints:
                c = p.rate.calcCost(fp.length, fp.duration)
                f += "Failed Print,,,{},{},{},{}\n".format(fp.length, fp.duration, r, c)
        
        return f


###################################################################################################
# Payment Class                                                                     Payment Class #
class Payment:
    # ----------------------------------------------------------------- Payment ------ __init__() #
    def __init__(self, userid, amt, auth_userid):
        assert type(userid) == str, "Expected 'str', got '{}'.".format(type(userid))
        assert type(amt) in {int, float}, "Expected number, got '{}'.".format(type(amt))
        assert type(auth_userid) == str, "Expected 'str', got '{}'.".format(type(auth_userid))
        
        self.userid = userid
        self.amt = amt
        self.auth_userid = auth_userid


###################################################################################################
# User Class                                                                           User Class #
class User:
    users = set()
    
    # -------------------------------------------------------------------- User ------ __init__() #
    def __init__(self, userid, passwd, email, issuper=False, firstname="", lastname=""):
        assert type(userid) == str, "Parameter 'userid' must be a string."
        assert type(passwd) == str, "Parameter 'passwd' must be a string."
        assert type(email) == str, "Parameter 'email' must be a string."
        assert type(issuper) == bool, "Parameter 'issuper' must be a boolean."
        assert type(firstname) == str, "Parameter 'firstname' must be a string."
        assert type(lastname) == str, "Parameter 'lastname' must be a string."
        
        u_logger.debug("__init__: Instantiating User object, userid={}".format(userid))
        self.userid = userid
        self.passwd = User.hash(passwd)
        self.email = email
        self.issuper = issuper
        self.firstname = firstname
        self.lastname = lastname
    
    
    # -------------------------------------------------------------------- User ---------- hash() #
    """ Hashes a string and returns the hash. Right now this function doesn't do anything, but when
    we implement password encryption, this is where that'll happen. """
    def hash(s):
        return s
    
    
    # -------------------------------------------------------------------- User ---------- dict() #
    """ Encodes the user object as a python dictionary. """
    def dict(self):
        d = dict()
        d["__class__"] = "User"
        d["userid"] = self.userid
        d["passwd"] = self.passwd
        d["email"] = self.email
        d["issuper"] = self.issuper
        d["firstname"] = self.firstname
        d["lastname"] = self.lastname
        return d
    
    
    # -------------------------------------------------------------------- User ------ fromDict() #
    """ Returns a User object whose attributes are taken from the values of a dictionary. """
    def fromDict(d):
        u = User(d["userid"], d["passwd"], d["email"], d["issuper"], d["firstname"], d["lastname"])
        return u
    
    
    # -------------------------------------------------------------------- User -------- encode() #
    """ Encodes the User object as a json string. """
    def encode(self):
        return json.dumps(self.dict())
    
    
    # -------------------------------------------------------------------- User -------- decode() #
    """ Decodes a User object from a json string. """
    def decode(code):
        d = json.loads(code)
        return User.fromDict(d)


###################################################################################################
# Server Request Class                                                       Server Request Class #
class ServerRequest:
    # ----------------------------------------------------------- ServerRequest ------ __init__() #
    def __init__(self, cmd, *args, **kwargs):
        self.cmd = cmd
        self.args = args
        self.kwargs = kwargs
    
    
    # ----------------------------------------------------------- ServerRequest -------- encode() #
    def encode(self):
        d = dict()
        d["cmd"] = self.cmd
        d["args"] = self.args
        d["kwargs"] = self.kwargs
        return json.dumps(d, default=serialize).encode("utf-8")
    
    
    # ----------------------------------------------------------- ServerRequest -------- decode() #
    def decode(s):
        try:
            d = json.loads(s, object_hook=deserialize)
        except:
            u_logger.exception("decode: error.")
            raise FormatError("Unable to extract JSON format from string.")
        missingkeys = set(d.keys()) - {"cmd", "args", "kwargs"}
        if missingkeys:
            raise ValueError("The following sections are missing from this request: {}".format(str(missingkeys)))
        return ServerRequest(d["cmd"], *d["args"], **d["kwargs"])


###################################################################################################
# Server Response Class                                                     Server Response Class #
class ServerResponse:
    # ---------------------------------------------------------- ServerResponse ------ __init__() #
    def __init__(self, val=None, err=False, errcode=0, errmsg = ""):
        self.val = val
        self.err = err
        self.errcode = errcode
        self.errmsg = errmsg
    
    
    # ---------------------------------------------------------- ServerResponse -------- encode() #
    def encode(self):
        d = dict()
        d["val"] = self.val
        d["err"] = self.err
        d["errcode"] = self.errcode
        d["errmsg"] = self.errmsg
        return json.dumps(d, default=serialize).encode("utf-8")
    
    
    # ---------------------------------------------------------- ServerResponse -------- encode() #
    """ Given the string s, which should be JSON formatted, returns an object. """
    def decode(s):
        try:
            d = json.loads(s, object_hook=deserialize)
            return ServerResponse(val=d["val"], err=d["err"], errcode=d["errcode"], errmsg=d["errmsg"])
        except Exception as e:
            res_logger.exception("decode: An error occured while decoding the response.")
            raise Exception(str(e))


"""JSON serializer for objects not serializable by default json code"""
def serialize(obj):
    if isinstance(obj, datetime):
        serial = {
                "__class__" : "datetime",
                "val" : obj.isoformat()
                }
        return serial

    if type(obj) in {PrintJob, PrintJob.FailedPrint, PrintRate, User}:
        serial = obj.dict()
        return serial
    
    try:
        return obj.__dict__
    except:
        pass
    
    try:
        return dict(obj)
    except:
        pass
    
    return str(obj)


def deserialize(d):
    if "__class__" in d.keys():
        c = d["__class__"]
        if c == "PrintJob":
            return PrintJob.fromDict(d)
        elif c == "PrintRate":
            return PrintRate.fromDict(d)
        elif c == "User":
            return User.fromDict(d)
        elif c == "datetime":
            return datetime.fromisoformat(d["val"])
    return d

class FormatError(SyntaxError):
    pass