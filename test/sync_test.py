# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0

# this test is only running on POSIX systems


import os, pathlib, sys
from optparse import OptionParser


def test_for(path):
    cwd = os.getcwd();
    os.chdir(path)
    os.environ["HOME"] = os.getcwd()

    print("running tests for " + path);
    from sync_handshake import run
    run()

    os.chdir(cwd)


def setup(path):
    cwd = os.getcwd();

    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    lib_path = os.path.join(os.environ["HOME"], "lib")
    Library_path = os.path.join(os.environ["HOME"], "Library")

    try:
        os.symlink(lib_path, "lib", True)
    except FileExistsError:
        pass

    try:
        os.symlink(Library_path, "Library", True)
    except FileExistsError:
        pass

    os.chdir(cwd)


def rmrf(path):
    try:
        for p in pathlib.Path(path).iterdir():
            if p.is_dir() and not p.is_symlink():
                rmrf(str(p))
            else:
                p.unlink()
        os.rmdir(path)
    except FileNotFoundError:
        pass


EINTR = 4


def waitpid(pid):
    e = EINTR
    while e == EINTR:
        try:
            pid, r = os.waitpid(pid, 0)
            if r:
                e = os.errno()
        except ChildProcessError:
            return


optParser = OptionParser()
optParser.add_option("-c", "--clean", action="store_true", dest="clean")
(options, args) = optParser.parse_args()

if options.clean:
    rmrf("alice")
    rmrf("bob")

else:
    setup("alice")
    setup("bob")

    alice = os.fork()
    if alice == 0:
        test_for("alice")
    else:
        bob = os.fork()
        if bob == 0:
            test_for("bob")
        else:
            waitpid(alice)
            waitpid(bob)

