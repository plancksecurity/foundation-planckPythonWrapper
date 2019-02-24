# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import os
import pathlib


def test_for(path):
    cwd = os.getcwd();
    os.chdir(path)
    os.environ["HOME"] = os.getcwd()

    print("running tests for " + path);
    from sync_handshake import run
    run(path)

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


if __name__ == "__main__":
    from optparse import OptionParser
    from multiprocessing import Process

    optParser = OptionParser()
    optParser.add_option("-c", "--clean", action="store_true", dest="clean",
            help="remove all generated files")
    options, args = optParser.parse_args()

    if options.clean:
        rmrf("TestInbox")
        rmrf("Alice")
        rmrf("Barbara")

    else:
        os.makedirs("TestInbox", exist_ok=True)
        setup("Alice")
        setup("Barbara")

        Alice = Process(target=test_for, args=("Alice",))
        Barbara = Process(target=test_for, args=("Barbara",))

        Alice.start()
        Barbara.start()

        Alice.join()
        Barbara.join()

