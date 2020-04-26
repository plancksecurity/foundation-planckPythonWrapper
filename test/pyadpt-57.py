#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This test is related to jira issue PYADPT-57 - key_mistrusted
# When key_mistrusted on own key (that has a private), a key revocation is being performed
# So, this test just proves the revocation by showing fpr before and after key_mistrusted()

"""
>>> alice = pEp.Identity("alice@peptest.org", "23")
>>> pEp.myself(alice)
>>> alice.fpr
>>> alice.key_mistrusted()
>>> pEp.myself(alice)
>>> alice.fpr
"""

import  pEp;

if __name__ == "__main__":
    import doctest
    doctest.testmod()
