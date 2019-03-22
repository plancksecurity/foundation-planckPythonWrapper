# vim: set fileencoding=utf-8 :

"""provide a trivial way to send messages between processes

messages are being sent as files to an inbox, which is a path of a directory,
using a filename as a marker

recv_all() is delivering all messages, which are newer than the marker file
after completion reading is touching the marker file

to re-read messages touch the marker file with an older timestamp or just
delete the marker file to re-read all messages

"""

# Minimail
# Copyleft 2019, p≡p foundation

# this file is under GNU General Public License 3.0


from secrets import token_urlsafe
from time import sleep


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
            sleep(1)
        lockfile.touch()


def send(inbox, msg, marker):
    "send msg to inbox in MIME format"

    with Lock(inbox):
        name = marker + "_" + token_urlsafe(16) + ".eml"
        with open(inbox / name, "wb") as f:
            f.write(str(msg).encode())


def newer(file1, file2):
    "return True if file1 is newer than file2"

    if not file1.is_file():
        return False
    elif not file2.is_file():
        return True

    stat1 = file1.stat()
    stat2 = file2.stat()
    return stat1.st_mtime > stat2.st_mtime


def recv_all(inbox, marker):
    """receive a list of new MIME messages from inbox, which are newer than the
    marker file"""

    r = []
    while not r:
        for p in reversed([ path for path in inbox.glob("*.eml") ]):
            if newer(p, inbox / marker):
                with Lock(inbox):
                    with open(p, "rb") as f:
                        t = f.read(-1)
                        r.append(t)
        if not r:
            sleep(1)

    (inbox / marker).touch(exist_ok=True)
    return r

