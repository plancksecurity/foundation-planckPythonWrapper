# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

module_pEp = Extension('pEp',
        sources = ['src/pEpmodule.cc',],
        include_dirs = ['/Users/vb/include',],
        library_dirs = ['/Users/vb/lib',],
        libraries = ['pEpEngine',],
    )

setup(
        name='p≡p Python adapter',
        version='1.0',
        description='Provides a Python module giving access to p≡p engine',
        author="Volker Birk",
        author_email="vb@pep-project.org",
        ext_modules=[module_pEp]
    )
