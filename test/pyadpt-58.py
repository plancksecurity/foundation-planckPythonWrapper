#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This test is related to jira issue PYADPT-58 - export keys

"""
>>> alice = pEp.Identity("alice@peptest.org", "23")
>>> pEp.myself(alice)
>>> pEp.export_key(alice)
"""

import  pEp;

if __name__ == "__main__":
    import doctest
    doctest.testmod()
