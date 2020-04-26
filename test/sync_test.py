#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""test runner for sync tests

Start this with:

$ python3 sync_test.py

"""

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import os
import sys
import shutil
import pathlib


def test_for(path, color=None, end_on=None, mt=False, imap=False, own_ident=1):

    cwd = os.getcwd();
    os.chdir(path)
    os.environ["HOME"] = os.getcwd()

    print("running tests for " + path)
    import sync_handshake
    if end_on:
        sync_handshake.end_on = end_on
    sync_handshake.multithreaded = mt

    sync_handshake.run(path, color, imap, own_ident)

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
    optParser.add_option("-n", "--noend", action="store_true", dest="noend",
            help="do not end")
    optParser.add_option("-E", "--end-on", dest="notifications",
            help="end test on these notifications")
    optParser.add_option("-3", "--third-device", action="store_true", dest="third",
            help="start Pad as third device")
    optParser.add_option("-j", "--multi-threaded", action="store_true",
            dest="multithreaded",
            help="use multithreaded instead of single threaded implementation")
    optParser.add_option("-i", "--imap", action="store_true",
            dest="imap",
            help="use imap instead of minimail")
    optParser.add_option("-A", "--add-account-after-sync", action="store_true",
            dest="add_account",
            help="after sync add an account")

    options, args = optParser.parse_args()

    if options.imap:
        import miniimap

    if options.cleanall:
        options.clean = True

    if options.clean:

        if options.imap:
            miniimap.clean_inbox()

            if options.cleanall:
                rmrf("Backup")
    
        else:
            rmrf("TestInbox")
            rmrf("Phone")
            rmrf("Laptop")
            rmrf("Pad")
            
            if options.cleanall:
                rmrf("Backup")

            if options.setup_only:
                os.makedirs("TestInbox", exist_ok=True)
                setup("Phone")
                setup("Laptop")
                if options.third:
                    setup("Pad")

    elif options.backup:
        rmrf("Backup")

        try:
            os.mkdir("Backup")
        except FileExistsError:
            pass

        if options.imap:
            try:
                os.mkdir("Backup/TestInbox")
            except FileExistsError:
                pass

            miniimap.backup_inbox()
        else:
            shutil.copytree("Phone", "Backup/Phone", symlinks=True, copy_function=shutil.copy2)
            shutil.copytree("Laptop", "Backup/Laptop", symlinks=True, copy_function=shutil.copy2)
            shutil.copytree("TestInbox", "Backup/TestInbox", symlinks=True, copy_function=shutil.copy2)
            try:
                shutil.copytree("Pad", "Backup/Pad", symlinks=True, copy_function=shutil.copy2)
            except FileNotFoundError:
                pass


    elif options.restore:
        if options.imap:
            miniimap.clean_inbox()
            miniimap.restore_inbox()
        else:
            rmrf("TestInbox")
            rmrf("Phone")
            rmrf("Laptop")
            rmrf("Pad")

            shutil.copytree("Backup/Phone", "Phone", symlinks=True, copy_function=shutil.copy2)
            shutil.copytree("Backup/Laptop", "Laptop", symlinks=True, copy_function=shutil.copy2)
            shutil.copytree("Backup/TestInbox", "TestInbox", symlinks=True, copy_function=shutil.copy2)
            try:
                shutil.copytree("Backup/Pad", "Pad", symlinks=True, copy_function=shutil.copy2)
            except FileNotFoundError:
                pass

    elif options.print:
        from sync_handshake import print_msg

        inbox = pathlib.Path("TestInbox")
        l = [ path for path in inbox.glob("*.eml") ]
        l.sort(key=(lambda p: p.stat().st_mtime))
        for p in l:
            print_msg(p)

    else:
        from multiprocessing import Process

        os.makedirs("TestInbox", exist_ok=True)
        setup("Phone")
        setup("Laptop")
        if options.third:
            setup("Pad")

        if not options.setup_only:
            end_on = None
            if options.notifications:
                end_on = eval(options.notifications)
                try: None in end_on
                except TypeError:
                    end_on = (end_on,)
            elif options.noend:
                end_on = (None,)

            # Phone runs with own_ident = 2
            Phone = Process(target=test_for, args=("Phone", "red", end_on,
                options.multithreaded, options.imap, 1))

            # others run with own_ident = 1
            Laptop = Process(target=test_for, args=("Laptop", "green", end_on,
                options.multithreaded, options.imap))
            if options.third:
                Pad = Process(target=test_for, args=("Pad", "cyan", end_on,
                    options.multithreaded, options.imap))

            Phone.start()
            Laptop.start()
            if options.third:
                Pad.start()

            Phone.join()
            Laptop.join()
            if options.third:
                Pad.join()
