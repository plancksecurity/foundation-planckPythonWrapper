# -*- coding: utf-8 -*-

# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

from __future__ import print_function

import sys
from sys import argv

import os
from os import environ, uname
from os.path import dirname, exists, join

from setuptools import setup, Extension
from glob import glob
import sysconfig

if sys.platform == 'winnt':
    if  sys.version_info[0] >= 3:
        import winreg
    else:
        import _winreg as winreg
        

from setuptools.command.build_ext import build_ext


if sys.version_info[0] < 3:
    FileNotFoundError = EnvironmentError

def find(fname, pathlist):
    for path in pathlist:
        cand_fname = join(path, fname)
        if exists(cand_fname):
            return path
    raise FileNotFoundError(fname)

def append_once(lst, element):
    if element not in lst:
        lst.append(element)

def extend_once(lst, elements):
    for element in elements:
        if element not in lst:
            lst.append(element)

def getPythonLibver():
    g = sysconfig.get_config_vars()
    sent = []
    for template in (
            '{cmd}{py_version_nodot}{abiflags}',
            '{cmd}{py_version_nodot}',
            '{cmd}{py_version_major}',
            '{cmd}{py_version_major}{abiflags}',
            '{cmd}'
        ):
        val = template.format(
            cmd = g['PYTHON'],
            py_version_nodot = g['py_version_nodot'],
            py_version_major = sys.version_info[0],
            abiflags = g.get('ABIFLAGS', ''),
        )
        if val not in sent:
            yield val
            sent.append(val)


class BuildExtCommand(build_ext):

    # default_pyver = next( getPythonLibver() )
    user_options = build_ext.user_options + [
        # ('boost-python=', None, 'Boost Python version to use (e.g. \'python34\')'),
        ('local', None, 'Use local pEp install in HOME/USERPROFILE'),
        ('with-pEp-engine=', None, 'Path to pEp Engine source'),
        ('with-pEp-libadapter=', None, 'Path to pEp C++ Adapter Library source'),
        ('with-boost=', None, 'Path to Boost install prefix'),
        ('with-asn1c-share=', None, 'Path to installed ASN1C share directory'),
    ]

    def windowsGetInstallLocation():
        # Note: should be installed to 'C:\Program Files (x86)' while a 32-bit distro
        # TODO: Try desktop adapter location first, then COM server
        # FIXME: This is wrong, we should chase the COM server, not the Outlook Plugin (even if they're in the same place)
        REG_PATH = "Software\\Microsoft\\Office\\Outlook\\Addins\\pEp"
        regKey = None
        try:
            regKey = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
            # Keys: Description, FileName, FriendlyName, LoadBehavior
            com_server, regtype = winreg.QueryValueEx(regKey, 'FileName')
            winreg.CloseKey(regKey)
        except WindowsError:
            com_server = None
        finally:
            if winreg:
                winreg.CloseKey(regKey)
        # <install-base>\\bin\\COM_Server.exe
        dirname = os.path.dirname
        return dirname( dirname( com_server ) )
        
    def initialize_options(self):
        build_ext.initialize_options(self)
        # self.boost_python = BuildExtCommand.default_pyver
        self.local = None != environ.get('PER_USER_DIRECTORY')
        self.with_pEp_engine = None
        self.with_pEp_libadapter = None
        self.with_boost = None
        self.with_asn1c_share = None

    def finalize_options(self):
        build_ext.finalize_options(self)

        # normalize paths given by user (expand tilde etc.)
        for with_option in ('pEp_engine', 'pEp_libadapter', 'boost', 'asn1c_share'):
            w_opt = 'with_' + with_option
            w_val = getattr(self, w_opt)
            if w_val != None:
                setattr(self, w_opt, os.path.normpath(w_val))

        if sys.platform == 'darwin':
            HOME = environ.get('PER_USER_DIRECTORY') or environ.get('HOME')
            PEPLIBNAME = 'libpEpEngine.dylib'
            LIBPEPA = 'libpEpAdapter.a'
            BOOSTLIBNAME = 'libboost_{boost_python:s}-mt.dylib'
            SYS_INCLUDES = [
                '/opt/local/include',   # we prefer MacPorts over Homebrew (but support both)
                '/usr/local/include',
                '/Library/Frameworks/PrettyEasyPrivacy.framework/Versions/A/include',
                join(environ["HOME"], 'include'),
                '/usr/include',
            ]
            SYS_SHARES = [
                '/opt/local/share',
                '/usr/local/share',
                '/Library/Frameworks/PrettyEasyPrivacy.framework/Versions/A/share',
                join(environ["HOME"], 'share'),
                '/usr/share',
            ]
            SYS_LIB_PREFIXES = [
                '/opt/local/lib',
                '/usr/local/lib',
                '/Library/Frameworks/PrettyEasyPrivacy.framework/Versions/A/lib',
                join(environ["HOME"], 'lib'),
                '/usr/lib',
            ]
        elif sys.platform == 'winnt':
            HOME = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
            SYS_ROOT = environ.get('SystemRoot')
            PROFILE_ROOT = environ.get('AppData')
            LOCAL_ROOT = environ.get('LocalAppData')
            INST_PREFIX = windowsGetInstallLocation()
            PEPLIBNAME = 'pEpEngine.dll'
            LIBPEPA = 'libpEpAdapter.a'
            BOOSTLIBNAME = 'boost_{boost_python:s}-mt.dll'
            SYS_INCLUDES = [
                join(INST_PREFIX, 'include'),
                join(PROFILE_ROOT, 'pEp', 'include'),
                join(LOCAL_ROOT, 'pEp', 'include'),
                join(SYS_ROOT, 'pEp', 'include'),
            ]
            SYS_SHARES = [
                join(INST_PREFIX, 'share'),
                join(PROFILE_ROOT, 'pEp', 'share'),
                join(LOCAL_ROOT, 'pEp', 'share'),
                join(SYS_ROOT, 'pEp', 'share'),
            ]
            SYS_LIB_PREFIXES = [
                join(INST_PREFIX, 'bin'),
                join(PROFILE_ROOT, 'pEp', 'bin'),
                join(LOCAL_ROOT, 'pEp', 'bin'),
                join(SYS_ROOT, 'pEp', 'bin'),
            ]
        else:
            HOME = environ.get('PER_USER_DIRECTORY') or environ.get('HOME')
            PEPLIBNAME = 'libpEpEngine.so'
            LIBPEPA = 'libpEpAdapter.a'
            BOOSTLIBNAME = 'libboost_python37.so'
            SYS_INCLUDES = ['/usr/local/pEp/include', '/usr/local/include', '/usr/include']
            SYS_SHARES = ['/usr/local/pEp/share', '/usr/local/share', '/usr/share']
            SYS_LIB_PREFIXES = ['/usr/local/pEp/bin', '/usr/local/bin', '/usr/bin', '/usr/lib/x86_64-linux-gnu/']

        use_local_incl = (self.local or os.path.isfile(
            join(HOME, 'include', 'pEp', 'pEpEngine.h')) )
        use_local_lib = (self.local or os.path.isfile(
            join(HOME, 'lib', PEPLIBNAME)) )

        INCLUDES = [ join(HOME, 'include') ] if use_local_incl else []
        INCLUDES.extend(SYS_INCLUDES)
        SHARES = [ join(HOME, 'share') ] if use_local_incl else []
        SHARES.extend(SYS_SHARES)
        LIBS = [ join(HOME, 'lib') ] if use_local_lib else []
        LIBS.extend(SYS_LIB_PREFIXES)

        if not self.with_pEp_engine:
            ENGINE_INC = find( join('pEp', 'pEpEngine.h'), INCLUDES )
            ENGINE_LIB = find( PEPLIBNAME, LIBS )
        else:
            if exists( join(self.with_pEp_engine, 'include', 'pEp') ):
                ENGINE_INC = find( join('pEp', 'pEpEngine.h'), (join(self.with_pEp_engine, 'include'),) )
                ENGINE_LIB = find( PEPLIBNAME, (join(self.with_pEp_engine, 'lib'),) )
            else:
                ENGINE_INC = find( 'pEpEngine.h', (join(self.with_pEp_engine, 'src'),) )
                ENGINE_LIB = find( PEPLIBNAME, (join(self.with_pEp_engine, 'src'),) )

        if not self.with_pEp_libadapter:
            LIBPEPA_INC = find( join('pEp', 'Adapter.hh'), INCLUDES )
            LIBPEPA_LIB = find( LIBPEPA, LIBS )
        else:
            if exists( join(self.with_pEp_libadapter, 'include', 'pEp') ):
                LIBPEPA_INC = find( join('pEp', 'Adapter.hh'), (join(self.with_pEp_libadapter, 'include'),) )
                LIBPEPA_LIB = find( LIBPEPA, (join(self.with_pEp_libadapter, 'lib'),) )
            else:
                LIBPEPA_INC = find( 'Adapter.hh', (join(self.with_pEp_libadapter, 'src'),) )
                LIBPEPA_LIB = find( LIBPEPA, (join(self.with_pEp_libadapter, 'src'),) )

        if not self.with_boost:
            BOOST_INC = find( join('boost', 'system', 'config.hpp'), INCLUDES )
            BOOST_LIB = None
            e_ = None
            for py in getPythonLibver():
                f = BOOSTLIBNAME.format(boost_python=py)
                try:
                    BOOST_LIB = find( f, LIBS )
                    break
                except Exception as e:
                    if self.verbose:
                        print("Not found: " + f)
                    e_ = e if e_ is None else e_
            if BOOST_LIB is None:
                raise e_
        else:
            raise NotImplementedError("Building from Boost source not implemented yet")   # FIXME
            # BOOST_INC = find( join('boost', 'system', 'config.hpp'), (self.with_boost,) )
            # BOOST_LIB = find( BOOSTLIBNAME, (self.with_boost,) )

        if not self.with_asn1c_share:
            ASN1C_INC = find( join('asn1c', 'asn_system.h'), SHARES )
        else:
            ASN1C_INC = find( join('asn1c', 'asn_system.h'), (self.with_asn1c_share,) )

        if self.verbose:
            print('ENGINE_INC=%s' % ENGINE_INC)
            print('ENGINE_LIB=%s' % ENGINE_LIB)
            print('LIBPEPA_INC=%s' % LIBPEPA_INC)
            print('LIBPEPA_LIB=%s' % LIBPEPA_LIB)
            print('BOOST_INC=%s' % BOOST_INC)
            print('BOOST_LIB=%s' % BOOST_LIB)
            print('ASN1C_INC=%s' % ASN1C_INC)

        global module_pEp
        extend_once( module_pEp.include_dirs, [ENGINE_INC, LIBPEPA_INC, BOOST_INC, ASN1C_INC] )
        extend_once( module_pEp.library_dirs, [ENGINE_LIB, LIBPEPA_LIB, BOOST_LIB] )
        extend_once( module_pEp.libraries, ['pEpEngine', 'boost_python3', 'boost_locale'] )

        if self.debug:
            module_pEp.extra_compile_args = ['-O0', '-g', '-UNDEBUG', '-std=c++14']
        else:
            module_pEp.extra_compile_args = ['-std=c++14']  # FIXME

    def run(self):
        build_ext.run(self)


# module_pEp global is referenced in BuildExtCommand
module_pEp = Extension('pEp',
        sources = glob('src/*.cc'),
        libraries = ['pEpEngine'],
        # extra_compile_args = compile_args,
        # include_dirs = [ENGINE_INC, BOOST_INC, ASN1C_INC],
        # library_dirs = [ENGINE_LIB, BOOST_LIB],
    )


setup(
        name='pEp',
        version='2.0',
        description='p≡p for Python',
        author="Volker Birk",
        author_email="vb@pep-project.org",
        ext_modules=[module_pEp,],
        cmdclass={
            'build_ext': BuildExtCommand,
        },
    )
