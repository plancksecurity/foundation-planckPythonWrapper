#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Regression test against API breakage
# colors used to be represented as a simple int
# NEW: colors are represented by colorvalue enum
# Test for equal resolution of colors using int (OLD) vs using colorvalue (NEW)

print("Running PYADPT-55")
"""
>>> resolveOLDvsNEW(pEp.colorvalue.no_color)
True
>>> resolveOLDvsNEW(pEp.colorvalue.yellow)
True
>>> resolveOLDvsNEW(pEp.colorvalue.green)
True
>>> resolveOLDvsNEW(pEp.colorvalue.red)
True
"""


import pEp
# resolves a color represented as int, the OLD way, as an int.
# returns colorvalue
def resolveColorOLD(col):
    ret = pEp.colorvalue()

    c = pEp.colorvalue(col)
    if(c == 0):
        ret = pEp.colorvalue.no_color
    if(c == 1):
        ret = pEp.colorvalue.yellow
    if(c == 2):
        ret = pEp.colorvalue.green
    if(c == -1):
        ret = pEp.colorvalue.red

    return ret

# resolves a color represented as colorvalue, the NEW way
# returns colorvalue
def resolveColorNEW(col):
    c = pEp.colorvalue(col)
    return c

# Compare color resolution OLD vs NEW way
# return True if results are equal
def resolveOLDvsNEW(col):
    return resolveColorOLD(col) == resolveColorNEW(col)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
