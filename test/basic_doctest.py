"""
>>> from pEp import *
>>> m = outgoing_message(Identity("vb@dingens.org", "23", "Volker Birk"))
>>> m.to = [Identity("trischa@dingens.org", "42", "Patricia Bednar")]
>>> m.shortmsg = "Hello"
>>> m.longmsg = "Something\\n"
>>> print(str(m).replace('\\r', ''))
From: Volker Birk <vb@dingens.org>
To: Patricia Bednar <trischa@dingens.org>
Subject: Hello
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="msg.txt"
<BLANKLINE>
Something
<BLANKLINE>
>>>
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
