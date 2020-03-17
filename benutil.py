# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:19:44 2020

@author: Ben
"""

from datetime import datetime

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

def types(*args):
    vals = tuple([type(a) for a in args])
    return vals


def datefstr(s):
    fmt1, fmt2 = "%Y-%m-%d %H:%M", "%Y-%m-%d"
    
    try:
        return datetime.strptime(s, fmt1)
    except:
        pass
    try:
        return datetime.strptime(s, fmt2)
    except:
        raise ValueError("String '{}' doesn't match format '{}' or '{}'.".format(s, fmt1, fmt2))

def isdate(s):
    try:
        datefstr(s)
    except ValueError:
        return False
    return True