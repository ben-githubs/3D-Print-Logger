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
    
    
    ###############################################################################################
    #                                                                            Server Functions #
    
    # --------------------------------------------------------------------------------- PrintJobs #
    def print_add(self, *args, **kwargs):
        return self.sendRequest(self.com.print.add, *args, **kwargs)
    
    def print_edit(self, *args, **kwargs):
        return self.sendRequest(self.com.print.edit, *args, **kwargs)
    
    def print_delete(self, *args, **kwargs):
        return self.sendRequest(self.com.print.delete, *args, **kwargs)
    
    def print_get(self, *args, **kwargs):
        return self.sendRequest(self.com.print.get, *args, **kwargs)
    
    def print_add_failed(self, *args, **kwargs):
        return self.sendRequest(self.com.print.add_failed, *args, **kwargs)
    
    def print_delete_failed(self, *args, **kwargs):
        return self.sendRequest(self.com.print.delete_failed, *args, **kwargs)
    
    
    # --------------------------------------------------------------------------------- PrintRate #
    def rate_add(self, *args, **kwargs):
        return self.sendRequest(self.com.rate.add, *args, **kwargs)
    
    def rate_delete(self, *args, **kwargs):
        return self.sendRequest(self.com.rate.delete, *args, **kwargs)
    
    def rate_get(self, *args, **kwargs):
        return self.sendRequest(self.com.rate.get, *args, **kwargs)
    
    
    # ----------------------------------------------------------------------------------- Printer #
    def printer_add(self, *args, **kwargs):
        return self.sendRequest(self.com.printer.add, *args, **kwargs)
    
    def printer_edit(self, *args, **kwargs):
        return self.sendRequest(self.com.printer.edit, *args, **kwargs)
    
    def printer_delete(self, *args, **kwargs):
        return self.sendRequest(self.com.printer.delete, *args, **kwargs)
    
    def printer_get(self, *args, **kwargs):
        return self.sendRequest(self.com.printer.get, *args, **kwargs)
    
    
    # ------------------------------------------------------------------------------------- Users #
    def user_add(self, *args, **kwargs):
        return self.sendRequest(self.com.user.add, *args, **kwargs)
    
    def user_edit(self, *args, **kwargs):
        return self.sendRequest(self.com.user.edit, *args, **kwargs)
    
    def user_delete(self, *args, **kwargs):
        return self.sendRequest(self.com.user.delete, *args, **kwargs)
    
    def user_get(self, *args, **kwargs):
        return self.sendRequest(self.com.user.get, *args, **kwargs)
    
    def user_verify(self, *args, **kwargs):
        return self.sendRequest(self.com.user.verify, *args, **kwargs)
    
    def user_issuper(self, *args, **kwargs):
        return self.sendRequest(self.com.user.issuper, *args, **kwargs)
        

if __name__ == "__main__":
    c = Client()
    c.connect()
    c.send(input(">> ").encode("utf-8"))
    input("Press <ENTER> to quit.")