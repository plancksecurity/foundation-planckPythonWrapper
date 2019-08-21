# -*- coding: utf-8 -*-

# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt


from setuptools import setup, Extension
from glob import glob
from os import environ
from os.path import dirname, exists, join, abspath
from sys import argv, platform


compile_args = ['-O0', '-g', '-UNDEBUG', '-std=c++14'] \
        if '--debug' in argv or '-g' in argv else ['-std=c++14']


def find(file, pathlist):
    for path in pathlist:
        _file = join(path, file)
        if exists(_file):
            return dirname(_file)
    raise FileNotFoundError(file)


includes = [
        join(environ['HOME'], 'include'),
        '/usr/include',
        '/usr/local/include',
        '/opt/local/include',
        join(environ['HOME'], 'share'),
        '/usr/share',
        '/usr/local/share',
        '/opt/local/share',
    ]


libraries = [
        join(environ['HOME'], 'lib'),
        '/usr/lib',
        '/usr/local/lib',
        '/opt/local/lib',
    ]


libext = '.dll' if platform == 'win32' else '.dylib' if platform == 'darwin' else '.so'


search_for_includes = 'pEp', 'boost', 'asn1c/asn_system.h'
search_for_libraries = 'libpEpengine' + libext, 'libboost_python3-mt' + libext


module_pEp = Extension('pEp',
        sources = glob('src/*.cc'),
        libraries = ['pEpEngine', 'boost_python3-mt', 'boost_locale-mt',],
        extra_compile_args = compile_args,
        include_dirs = list(set( [ find(file, includes) for file in
            search_for_includes ] )),
        library_dirs = list(set( [ find(file, libraries) for file in
            search_for_libraries ] )),
    )


setup(
        name='pEp',
        version='2.0',
        description='p≡p for Python',
        author="Volker Birk",
        author_email="vb@pep-project.org",
        ext_modules=[module_pEp,],
    )

