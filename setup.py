# -*- coding: utf-8 -*-

from distutils.core import setup, Extension
from glob import glob

prefix = '/Users/vb'
boost = '/opt/local'

module_pEp = Extension('pEp',
        sources = glob('src/*.cc'),
        include_dirs = [prefix+'/include', boost+'/include',],
        library_dirs = [prefix+'/lib', boost+'/lib',],
        libraries = ['pEpEngine', 'boost_python-mt', 'boost_locale-mt',],
        extra_compile_args = ['-O0', '-g',],
    )

setup(
        name='p≡p Python adapter',
        version='1.0',
        description='Provides a Python module giving access to p≡p engine',
        author="Volker Birk",
        author_email="vb@pep-project.org",
        ext_modules=[module_pEp]
    )
