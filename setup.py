# -*- coding: utf-8 -*-

import sys
import os
from distutils.core import setup, Extension
from glob import glob
from distutils.errors import DistutilsOptionError

def option_value(name):
    for index, option in enumerate(sys.argv):
        if option == '--' + name:
            if index+1 >= len(sys.argv):
                raise DistutilsOptionError(
                    'The option %s requires a value' % option)
            value = sys.argv[index+1]
            sys.argv[index:index+2] = []
            return value
        if option.startswith('--' + name + '='):
            value = option[len(name)+3:]
            sys.argv[index:index+1] = []
            return value
    env_val = os.getenv(name.upper().replace('-', '_'))
    return env_val

OPTION_PREFIX = option_value("prefix")
OPTION_BOOST = option_value("boost")

if OPTION_PREFIX is None :
    OPTION_PREFIX = os.environ["HOME"]

if OPTION_BOOST is None :
    OPTION_BOOST = '/opt/local'

module_pEp = Extension('pEp',
        sources = glob('src/*.cc'),
        include_dirs = [OPTION_PREFIX+'/include', OPTION_BOOST+'/include',],
        library_dirs = [OPTION_PREFIX+'/lib', OPTION_BOOST+'/lib',],
        libraries = ['pEpEngine', 'boost_python-mt', 'boost_locale-mt',],
        extra_compile_args = ['-O0', '-UNDEBUG', '-std=c++14',],
    )

setup(
        name='p≡p Python adapter',
        version='1.0',
        description='Provides a Python module giving access to p≡p engine',
        author="Volker Birk",
        author_email="vb@pep-project.org",
        ext_modules=[module_pEp]
    )
