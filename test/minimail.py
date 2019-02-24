# vim: set fileencoding=utf-8 :

# Minimail
# Copyleft 2019, p≡p foundation

# this file is under GNU General Public License 3.0


from secrets import token_urlsafe
from itertools import compress
from functools import partial
from time import sleep


def unlock(inbox):
    lockfile = inbox / "lock"
    try:
        lockfile.unlink()
    except:
        pass


class Lock:
    def __init__(self, inbox):
        self.inbox = inbox

    def __exit__(self, *exc):
        unlock(self.inbox)

    def __enter__(self):
        lockfile = self.inbox / "lock"
        while lockfile.is_file():
            sleep(1)
        lockfile.touch()


def send(inbox, msg):
    with Lock(inbox):
        name = token_urlsafe(16) + ".eml"
        with open(inbox / name, "wb") as f:
            f.write(str(msg).encode())


def newer(file1, file2=None):
    if not file1.is_file():
        return False
    elif not file2.is_file():
        return True

    stat1 = file1.stat()
    stat2 = file2.stat()
    return stat1.st_mtime > stat2.st_mtime


def recv_all(inbox, marker):
    with Lock(inbox):
        r = []
        while not r:
            for f in compress(inbox.glob("*.eml"), partial(newer, file2=marker)):
                t = f.readall()
                r.append(t)
            if not r:
                sleep(1)
        marker.touch(exist_ok=True)
    return r

