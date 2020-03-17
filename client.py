# stuff
"""
Copyright Ben Airey, 2020

Free to use and edit.
"""

import configparser
import logging
from random import randint
import socket

#import pycrypto

from commands import commands
from makerspace import ServerRequest, ServerResponse, ServerError

CONFIG_FILE = r"client.ini"

DEFAULT_HOST = "127.0.0.1" # Localhost
DEFAULT_PORT = 24571


class Client:
    def __init__(self):
        # First, load parameters from config file.
        self.conf = configparser.ConfigParser()
        self.conf.read(CONFIG_FILE)
        self.host = self.conf.get("CLIENT", "host")
        self.port = self.conf.getint("CLIENT", "port")
        
        self.logger = logging.getLogger("app.client.Client")
        
        # Next, set up some variables we'll be using later
        self.conn = None # This variable will house the connection to the server
        
        # Load command codes
        self.com = commands()
    
    
    """ Attempt to connect to the host. """
    def connect(self):
        self.logger.info("connect: Connecting to server...")
        host = self.host #DEFAULT_HOST#self.conf.get("host", DEFAULT_HOST)
        port = self.port #DEFAULT_PORT#self.conf.get("port", DEFAULT_PORT)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.conn = s
        self.key = None
        self.logger.info("connect: Done.")
    
    
    """ Send something to server and await response. """
    def send(self, data):
        self.logger.debug("send: Sending data...")
        self.conn.sendall(data)
        self.logger.debug("send: Data sent. Waiting for response...")
        resp = ""
        
        while True:
            resp += self.conn.recv(1024).decode("utf-8")
            if ServerResponse.END_SIGNAL in resp:
                resp = resp[:resp.find(ServerResponse.END_SIGNAL)]
                break
        self.logger.debug("send: Done.")
        return resp
    
    
    """ Send something to server and await response. """
    def getresp(self, request):
        assert type(request) == ServerRequest
        resp = ServerResponse.decode(self.send(request.encode().encode("utf-8")))
        if not resp.err:
            return resp.val
        else:
            raise ServerError(resp.errmsg)
    
    
    """ Closes the client socket. """
    def close(self):
        self.logger.debug("close: Closing socket...")
        if self.conn:
            self.conn.close()
        self.logger.debug("close: Done.")
    
    
    """ Sends a request to the server. """
    def sendRequest(self, cmd, *args, **kwargs):
        request = ServerRequest(cmd, *args, **kwargs)
        return self.getresp(request)
    
    
    """ Performs Diffie-Hellman handshake """
    def handshake(self):
        # Wait for server to send prime and g
        m = self.conn.recv(1024)
        p, g = m.split(",")
        p = int(p)
        g = int(g)
        # Generate a, A
        a = randint(10000,99999)
        A = g**a % p
        # Send to server, await response
        B = int(self.send(str(A)))
        # Calculate Key
        self.conn.key = B**a % p
    
    def encrypt(self, data):
        if not self.conn.key:
            return data
        
        
        
    
    
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
    
    def user_getowing(self, *args, **kwargs):
        return self.sendRequest(self.com.user.getowing, *args, **kwargs)
    
    # ----------------------------------------------------------------------------------- Invoice #
    def invoice_add(self, *args, **kwargs):
        return self.sendRequest(self.com.inv.add, *args, **kwargs)
    
    def invoice_get(self, *args, **kwargs):
        return self.sendRequest(self.com.inv.get, *args, **kwargs)
    
    def payment_log(self, *args, **kwargs):
        return self.sendRequest(self.com.inv.pay, *args, **kwargs)
        

if __name__ == "__main__":
    c = Client()
    c.connect()
    c.send(input(">> ").encode("utf-8"))
    input("Press <ENTER> to quit.")