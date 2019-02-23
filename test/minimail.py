# vim: set fileencoding=utf-8 :

# Minimail
# Copyleft 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import pEp
from secrets import token_urlsafe


def send(msg):
    name = token_urlsafe(16) + ".eml"
    with open("../TestInbox/" + name, "wb") as f:
        f.write(str(msg).encode())


def recv(msg):
    pass
