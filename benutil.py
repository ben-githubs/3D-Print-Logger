# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:19:44 2020

@author: Ben
"""

""" A shorteded version of a try-catch loop. Will try to execude cmd, and will display msg if an 
error occurs."""
def trycatch(cmd, msg=""):
    try:
        cmd
    except:
        raise AssertionError(msg)


class struct:
    pass

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False