# vim: set fileencoding=utf-8 :

"""provide a trivial way to send messages between processes

messages are being sent as files to an inbox, which is a path of a directory,
using a filename as a marker

recv_all() is delivering all messages, which are newer than the marker file
after completion reading is touching the marker file

to re-read messages touch the marker file with an older timestamp or just
delete the marker file to re-read all messages

"""

# Minimail 1.1
# Copyleft 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import os
from secrets import token_urlsafe
from time import sleep


timing = .1


def unlock(inbox):
    "clear the inbox from lockfile"

    lockfile = inbox / "lock"
    try:
        lockfile.unlink()
    except:
        pass


class Lock:
    "lock inbox context to be used by with statement"

    def __init__(self, inbox):
        self.inbox = inbox

    def __exit__(self, *exc):
        unlock(self.inbox)

    def __enter__(self):
        lockfile = self.inbox / "lock"
        while lockfile.is_file():
            sleep(timing)
        lockfile.touch()


def send(inbox, msg, marker):
    "send msg to inbox in MIME format"

    sleep(timing)
    with Lock(inbox):
        name = marker + "_" + token_urlsafe(16) + ".eml"
        with open(inbox / name, "wb") as f:
            f.write(str(msg).encode())


def newer(file, stamp):
    "return True if file is newer than timestamp stamp"

    if not file.is_file():
        return False
    
    if stamp is None:
        return True

    stat = file.stat()
    return stat.st_mtime > stamp.st_mtime


def recv_all(inbox, marker):
    """receive a list of new MIME messages from inbox, which are newer than the
    marker file"""

    r = []
    while not r:
        with Lock(inbox):
            try:
                stamp = (inbox / marker).stat()
            except:
                stamp = None
            l = [ path for path in inbox.glob("*.eml") ]
            (inbox / marker).touch(exist_ok=True)
            for p in reversed(l):
                if newer(p, stamp):
                    with open(p, "rb") as f:
                        txt = f.read(-1)
                        r.append((p, txt))
        if not r:
            sleep(timing)

    return r

