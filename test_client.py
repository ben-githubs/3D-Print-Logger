# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 19:48:50 2020

@author: Ben
"""

from client import Client
from server import Server

def main():
    client = Client()
    server = Server("server.ini")
    
    client.connect()
    
    quit = False
    while not quit:
        cmd = input(" >> ")
        
        if cmd == "quit":
            quit = True
        elif cmd.split(" ")[0] == "adduser":
            args = cmd.split(" ")[1:]
            if len(args) < 3:
                args.append(False)
                args.append("")
                args.append("")
            client.addUser(args[0], args[1], issuper=args[2], auth_userid=args[3], auth_passwd=args[4])
    
    server._kill = True
    client.close()

if __name__ == "__main__":
    main()