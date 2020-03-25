# Regression test against API breakage
# colors used to be represented as a simple int
# NEW: colors are represented by PEP_color enum
# Test for equal resolution of colors using int (OLD) vs using PEP_color (NEW)

"""
>>> resolveOLDvsNEW(pEp.PEP_color.PEP_color_no_color)
True
>>> resolveOLDvsNEW(pEp.PEP_color.PEP_color_yellow)
True
>>> resolveOLDvsNEW(pEp.PEP_color.PEP_color_green)
True
>>> resolveOLDvsNEW(pEp.PEP_color.PEP_color_red)
True
"""



import pEp
# resolves a color represented as int, the OLD way
# returns PEP_color
def resolveColorOLD(col):
    ret = pEp.PEP_color()

    c = pEp.PEP_color(col)
    if(c == 0):
        ret = pEp.PEP_color.PEP_color_no_color
    if(c == 1):
        ret = pEp.PEP_color.PEP_color_yellow
    if(c == 2):
        ret = pEp.PEP_color.PEP_color_green
    if(c == -1):
        ret = pEp.PEP_color.PEP_color_red

    return ret

# resolves a color represented as PEP_color, the NEW way
# returns PEP_color
def resolveColorNEW(col):
    c = pEp.PEP_color(col)
    return col

# Compare color resolution OLD vs NEW way
# return True if results are equal
def resolveOLDvsNEW(col):
    return resolveColorOLD(col) == resolveColorNEW(col)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
