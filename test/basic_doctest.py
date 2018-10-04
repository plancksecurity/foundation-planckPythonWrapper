"""
>>> import pEp
>>> me = pEp.Identity("alice.smith@peptest.ch", "23", "Alice Smith")
>>> me.username
'Alice Smith'
>>> print(me)
Alice Smith <alice.smith@peptest.ch>
>>> you = pEp.Identity("bob.bourne@peptest.ch", "42", "Bob Bourne")
>>> print(you)
Bob Bourne <bob.bourne@peptest.ch>
>>> m = pEp.outgoing_message(me)
>>> m.to = [you]
>>> m.shortmsg = "let's meet next week"
>>> m.longmsg = "Please call me back"
>>> print(str(m).replace('\\r', ''))
From: Alice Smith <alice.smith@peptest.ch>
To: Bob Bourne <bob.bourne@peptest.ch>
Subject: let's meet next week
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="msg.txt"
<BLANKLINE>
Please call me back
>>> m2 = m.encrypt()
>>> m3, keys, rating, flags = m2.decrypt()
>>> rating
3
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
