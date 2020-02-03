# stuff
"""
Copyright Ben Airey, 2020

Free to use and edit.
"""

import configparser
from enum import Enum
import json
import logging
import socket

from natsort import natsorted

from commands import commands
from makerspace import ServerRequest, ServerResponse, PrintRate, User

format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
c_logger = logging.getLogger("app.client.Client")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(format)
if not len(c_logger.handlers):
    c_logger.addHandler(ch)

CONFIG_FILE = r"client_config.ini"

DEFAULT_HOST = "127.0.0.1" # Localhost
DEFAULT_PORT = 24571


class RtnCode(Enum):
    SUCCESS = 0    # Return when everything goes well
    SYNTAX_ERR = 1 # Return if there's a problem parsing the command
    SERVER_ERR = 2 # Return if there was an error on the server trying to execute the command

""" Represent different types of server queries using enums! """
class CmdCode(Enum):
    NEW_LOG = 0
    NEW_LOG_FAILED = 1
    NEW_USER = 2
    USER_CHANGE_PASS = 3
    QUERY_LOG = 4



class Client:
    def __init__(self):
        # First, load parameters from config file.
        #self.conf = configparser.ConfigParser()
        #self.conf.read(CONFIG_FILE)
        
        # Next, set up some variables we'll be using later
        self.conn = None # This variable will house the connection to the server
        
        # Load command codes
        self.com = commands()
    
    """ Attempt to connect to the host. """
    def connect(self):
        c_logger.info("connect: Connecting to server...")
        host = DEFAULT_HOST#self.conf.get("host", DEFAULT_HOST)
        port = DEFAULT_PORT#self.conf.get("port", DEFAULT_PORT)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.conn = s
        c_logger.info("connect: Done.")
    
    """ Send something to server and await response. """
    def send(self, data):
        c_logger.debug("send: Sending data...")
        self.conn.sendall(data)
        c_logger.debug("send: Data sent. Waiting for response...")
        resp = self.conn.recv(1024) # Wait for response
        c_logger.debug("send: Done.")
        return resp
    
    
    """ Send something to server and await response. """
    def getresp(self, request):
        assert type(request) == ServerRequest
        resp = ServerResponse.decode(self.send(request.encode()))
        if not resp.err:
            return resp.val
        else:
            raise Exception(resp.errmsg)
        

    """ Closes the client socket. """
    def close(self):
        c_logger.debug("close: Closing socket...")
        if self.conn:
            self.conn.close()
        c_logger.debug("close: Done.")
    
    
    """ Sends a request to the server. """
    def sendRequest(self, cmd, *args, **kwargs):
        request = ServerRequest(cmd, *args, **kwargs)
        return self.getresp(request)
    
    
    # ---------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------- USER MANAGEMENT #
    
    # -------------------------------------------------------------------------------- user_add() #
    """ Add User """
    def user_add(self, userid, passwd, issuper=False, auth_userid="", auth_passwd="", email="", 
                firstname="", lastname=""):
        c_logger.info("user_add: Adding a new user.")
        
        msg = ServerRequest(cmd=self.com.user.add)
        msg.args = {
                "userid" : userid,
                "passwd" : passwd,
                "email" : email,
                "issuper" : issuper,
                "auth_userid" : auth_userid,
                "auth_passwd" : auth_passwd,
                "firstname" : firstname,
                "lastname" : lastname,
            }
        
        c_logger.debug("user_add: Sending request to server...")
        return self.getresp(msg)
    
    
    # ------------------------------------------------------------------------------- user_edit() #
    """ Makes changes to a user profile. """
    def user_edit(self, userid, auth_userid, auth_passwd, passwd="", issuper=None, email="", 
                 firstname="", lastname=""):
        msg = ServerRequest(cmd=self.com.user.edit)
        msg.args["userid"] = userid
        msg.args["auth_userid"] = auth_userid
        msg.args["auth_passwd"] = auth_passwd
        if passwd:
            msg.args["passwd"] = passwd
        if not issuper==None:
            msg.args["issuper"] = issuper
        if email:
            msg.args["email"] = email
        if firstname:
            msg.args["firstname"] = firstname
        if lastname:
            msg.args["lastname"] = lastname
        
        c_logger.debug("user_edit: Sending request to server...")
        return self.getresp(msg)
    
    
    # ----------------------------------------------------------------------------- user_delete() #
    """ Deletes one or more user profiles, based on their userid's. """
    def user_delete(self, userids, auth_userid, auth_passwd):
        msg = ServerRequest(cmd=self.com.user.edit)
        msg.args["userids"] = userids
        msg.args["auth_userid"] = auth_userid
        msg.args["auth_passwd"] = auth_passwd
        
        c_logger.debug("user_edit: Sending request to server...")
        return self.getresp(msg)
    
    
    # -------------------------------------------------------------------------------- user_get() #
    """ Given a set of search criteria, returns  """
    def user_get(self, **kwargs):
        msg = ServerRequest(cmd=self.com.user.get)
        msg.args = kwargs
        c_logger.debug("user_get: Sending request to server...")
        users = self.getresp(msg)
        return [User.fromDict(d) for d in users]
                
    
    # ------------------------------------------------------------------------------ verifyUser() #
    """ Verify if user credentials are legit. """
    def verifyUser(self, userid, passwd):
        c_logger.info("verifyUser: Verifying user credentials...")
        
        msg = ServerRequest(cmd=self.com.user.verify)
        msg.args["userid"] = userid
        msg.args["passwd"] = passwd
        
        c_logger.debug("verifyUser: Sending request to server...")
        resp = self.send(msg.encode())
        resp = ServerResponse.decode(resp)
        if not resp.err:
            return resp.val
        else:
            raise Exception(resp.errmsg)
    
    
    # --------------------------------------------------------------------------------- issuper() #
    """ Checks whether or not a user is a superuser. """
    def user_issuper(self, userid, passwd):
        c_logger.debug("issuper: Checking if '{}' is an elevated user.".format(userid))
        msg = ServerRequest(cmd=self.com.user.issuper)
        msg.args["userid"] = userid
        msg.args["passwd"] = passwd
        
        c_logger.debug("issuper: Sending request to server...")
        resp = ServerResponse.decode(self.send(msg.encode()))
        if not resp.err:
            c_logger.debug("issuper: Done.")
            return resp.val
        else:
            raise Exception(resp.errmsg)
    
    
    # -------------------------------------------------------------------------------- getUsers() #
    """ Returns a list of all users in the system. """
    def getUsers(self):
        msg = ServerRequest(cmd=self.com.user.getall)
        c_logger.debug("getUsers: Sending request to server...")
        resp = ServerResponse.decode(self.send(msg.encode()))
        if not resp.err:
            return resp.val
        else:
            raise Exception(resp.errmsg)
    
    
    # ---------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------- PRINTJOBS #
    """ Adds a new print job. """
    def print_add(self, userid, passwd, length, duration, printer, rate, paidby="", note=""):
        msg = ServerRequest(cmd=self.com.print.add)
        msg.args["userid"] = userid
        msg.args["passwd"] = passwd
        msg.args["length"] = length
        msg.args["duration"] = duration
        msg.args["printer"] = printer
        msg.args["rate"] = rate
        if paidby:
            msg.args["paidby"] = paidby
        if note:
            msg.args["note"] = note
        
        resp = ServerResponse.decode(self.send(msg.encode()))
        if not resp.err:
            return resp.val
        else:
            raise Exception(resp.errmsg)
        
        
    
    
    # ---------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------- PRINT RATES #
    """ Returns a list of all print rates. """
    def rate_getall(self):
        msg = ServerRequest(cmd=self.com.rate.getall)
        resp = ServerResponse.decode(self.send(msg.encode()))
        if not resp.err:
            assert type(resp.val) == list
            return natsorted([PrintRate.loadjson(r) for r in resp.val], key=lambda x: x.rateid)
        else:
            raise Exception(resp.errmsg)
    
    
    """ Adds a new print rate. """
    def rate_add(self, rateid, lengthrate, timerate, auth_userid, auth_passwd):
        msg = ServerRequest(cmd=self.com.rate.add)
        msg.args["rateid"] = rateid
        msg.args["lengthrate"] = lengthrate
        msg.args["timerate"] = timerate
        msg.args["auth_userid"] = auth_userid
        msg.args["auth_passwd"] = auth_passwd
        resp = ServerResponse.decode(self.send(msg.encode()))
        if resp.err:
            raise Exception(resp.errmsg)
    
    
    """ Adds a new printer. """
    def printer_add(self, printer, auth_userid, auth_passwd):
        msg = ServerRequest(cmd=self.com.printer.add)
        msg.args["printer"] = printer
        msg.args["auth_userid"] = auth_userid
        msg.args["auth_passwd"] = auth_passwd
        resp = ServerResponse.decode(self.send(msg.encode()))
        if resp.err:
            raise Exception(resp.errmsg)
    
    
    """ Remove a printer from the printer list. """
    def printer_delete(self, printer, auth_userid, auth_passwd):
        msg = ServerRequest(cmd=self.com.printer.delete)
        msg.args["printer"] = printer
        msg.args["auth_userid"] = auth_userid
        msg.args["auth_passwd"] = auth_passwd
        resp = ServerResponse.decode(self.send(msg.encode()))
        if resp.err:
            raise Exception(resp.errmsg)
    
    
    """ Returns a list of all printers. """
    def printer_getall(self):
        msg = ServerRequest(cmd=self.com.printer.getall)
        resp = ServerResponse.decode(self.send(msg.encode()))
        if not resp.err:
            assert type(resp.val) == list
            return natsorted(resp.val)
        else:
            raise Exception(resp.errmsg)
        

if __name__ == "__main__":
    c = Client()
    c.connect()
    c.send(input(">> ").encode("utf-8"))
    input("Press <ENTER> to quit.")