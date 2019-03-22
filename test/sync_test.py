# vim: set fileencoding=utf-8 :

"""test runner for sync tests

Start this with:

$ python3 sync_test.py

"""

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import os
import shutil
import pathlib


def test_for(path, color=None):
    cwd = os.getcwd();
    os.chdir(path)
    os.environ["HOME"] = os.getcwd()

    print("running tests for " + path)
    from sync_handshake import run
    run(path, color)

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

    optParser = OptionParser()
    optParser.description = __doc__
    optParser.add_option("-c", "--clean", action="store_true", dest="clean",
            help="remove all generated files")
    optParser.add_option("-b", "--backup", action="store_true", dest="backup",
            help="make a backup of all generated files (old backup will be overwritten)")
    optParser.add_option("-r", "--restore", action="store_true", dest="restore",
            help="restore generated files from backup")
    optParser.add_option("-C", "--clean-all", action="store_true", dest="cleanall",
            help="remove all generated files including backup files")
    optParser.add_option("-s", "--setup", action="store_true", dest="setup_only",
            help="setup environment, then stop")
    optParser.add_option("-p", "--print", action="store_true", dest="print",
            help="print sync message trace in inbox")
    options, args = optParser.parse_args()

    if options.cleanall:
        options.clean = True

    if options.clean:
        rmrf("TestInbox")
        rmrf("Phone")
        rmrf("Laptop")

        if options.cleanall:
            rmrf("Backup")

    elif options.backup:
        rmrf("Backup")

        try:
            os.mkdir("Backup")
        except FileExistsError:
            pass

        shutil.copytree("Phone", "Backup/Phone", symlinks=True, copy_function=shutil.copy2)
        shutil.copytree("Laptop", "Backup/Laptop", symlinks=True, copy_function=shutil.copy2)
        shutil.copytree("TestInbox", "Backup/TestInbox", symlinks=True, copy_function=shutil.copy2)

    elif options.restore:
        rmrf("TestInbox")
        rmrf("Phone")
        rmrf("Laptop")

        shutil.copytree("Backup/Phone", "Phone", symlinks=True, copy_function=shutil.copy2)
        shutil.copytree("Backup/Laptop", "Laptop", symlinks=True, copy_function=shutil.copy2)
        shutil.copytree("Backup/TestInbox", "TestInbox", symlinks=True, copy_function=shutil.copy2)

    elif options.print:
        from sync_handshake import print_msg

        inbox = pathlib.Path("TestInbox")
        for p in reversed([ path for path in inbox.glob("*.eml") ]):
            print_msg(p)
        
    else:
        from multiprocessing import Process

        os.makedirs("TestInbox", exist_ok=True)
        setup("Phone")
        setup("Laptop")

        if not options.setup_only:
            Phone = Process(target=test_for, args=("Phone", "red"))
            Laptop = Process(target=test_for, args=("Laptop", "green"))

            Phone.start()
            Laptop.start()

            Phone.join()
            Laptop.join()

