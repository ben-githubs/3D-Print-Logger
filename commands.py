# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 12:57:21 2020

@author: Ben
"""

from benutil import struct

""" Generates the command codes and returns the struct. """
def commands():
    cmd = struct()
    
    cmd.print = struct()
    cmd.print.add = "P1"
    cmd.print.edit = "P2"
    cmd.print.delete = "P3"
    cmd.print.get = "P4"
    cmd.print.add_failed = "P5"
    cmd.print.delete_failed = "P6"
    
    cmd.rate = struct()
    cmd.rate.add = "R1"
    cmd.rate.delete = "R2"
    cmd.rate.get = "R3"
    
    cmd.printer = struct()
    cmd.printer.add = "T1"
    cmd.printer.delete = "T2"
    cmd.printer.get = "T3"
    
    cmd.user = struct()
    cmd.user.add = "U1"
    cmd.user.edit = "U2"
    cmd.user.delete = "U3"
    cmd.user.get = "U4"
    cmd.user.verify = "U5"
    cmd.user.issuper = "U6"
    
    return cmd