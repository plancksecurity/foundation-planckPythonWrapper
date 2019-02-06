# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, Volker Birk

# this file is under GNU General Public License 3.0


import os


def setup(path):
    cwd = os.getcwd();

    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    lib_path = os.path.join(os.environ["HOME"], "lib")
    Library_path = os.path.join(os.environ["HOME"], "Library")

    os.chdir(cwd)
