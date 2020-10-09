# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt
#
# For more debugging, export DISTUTILS_DEBUG=True

from __future__ import print_function

import sys

import os
from os import environ
from os.path import join
import platform

from setuptools import setup, Extension
from glob import glob

from setuptools.command.build_ext import build_ext


def pEpLog(*msg):
    import inspect
    msgstr = ''
    separator = ' '
    for m in msg:
        msgstr += str(m)
        msgstr += separator
    func = inspect.currentframe().f_back.f_code
    print(func.co_filename + " : " + func.co_name + " : " + msgstr)


class BuildExtCommand(build_ext):
    user_options = build_ext.user_options + [
        ('local', None, 'Use local pEp install in HOME/USERPROFILE for libs/includes'),
        ('prefix=', None, 'Use local pEp install in prefix for libs/includes'),
    ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.local = None != environ.get('PER_USER_DIRECTORY')
        self.prefix = getattr(self, "prefix=", None)

    def windowsGetInstallLocation(self):
        # Note: should be installed to 'C:\Program Files (x86)' while a 32-bit distro
        # TODO: Try desktop adapter location first, then COM server
        # FIXME: This is wrong, we should chase the COM server, not the Outlook Plugin (even if they're in the same place)
        reg_path = "Software\\Microsoft\\Office\\Outlook\\Addins\\pEp"
        KeyName = 'FileName'
        regKey = None
        pEpLog("Registry Lookup:", reg_path, KeyName)
        try:
            regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
            # Keys: Description, FileName, FriendlyName, LoadBehavior
            com_server, regtype = winreg.QueryValueEx(regKey, KeyName)
            winreg.CloseKey(regKey)
        except WindowsError:
            pEpLog("Unknown Error")
            com_server = None
        finally:
            if winreg:
                winreg.CloseKey(regKey)
        # <install-base>\\bin\\COM_Server.exe
        dirname = os.path.dirname
        ret = dirname(dirname(com_server))
        pEpLog("Value:", ret)
        return ret

    def get_build_info_winnt(self):
        home = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
        sys_root = environ.get('SystemRoot')
        profile_root = environ.get('AppData')
        local_root = environ.get('LocalAppData')
        inst_prefix = self.windowsGetInstallLocation()
        sys_includes = [
            join(inst_prefix, 'include'),
            join(profile_root, 'pEp', 'include'),
            join(local_root, 'pEp', 'include'),
            join(sys_root, 'pEp', 'include'),
        ]
        sys_libdirs = [
            join(inst_prefix, 'bin'),
            join(profile_root, 'pEp', 'bin'),
            join(local_root, 'pEp', 'bin'),
            join(sys_root, 'pEp', 'bin'),
        ]
        libs = [
            'pEpEngine',
            'pEpAdapter',
            'boost_python37-mt',
            'boost_locale-mt'
        ]
        return (home, sys_includes, sys_libdirs, libs)

    def get_build_info_darwin(self):
        home = environ.get('PER_USER_DIRECTORY') or environ.get('HOME')
        sys_includes = [
            '/opt/local/include',
        ]
        sys_libdirs = [
            '/opt/local/lib',
        ]
        libs = [
            'pEpEngine',
            'pEpAdapter',
            'boost_python38-mt',
            'boost_locale-mt'
        ]
        return (home, sys_includes, sys_libdirs, libs)

    def get_build_info_linux(self):
        home = environ.get('PER_USER_DIRECTORY') or environ.get('HOME')
        sys_includes = [
            '/usr/local/include',
            '/usr/include',
        ]
        sys_libdirs = [
            '/usr/local/lib',
            '/usr/lib',
            '/usr/lib/{}-linux-gnu'.format(platform.machine())
        ]
        libs = [
            'pEpEngine',
            'pEpAdapter',
            'boost_python3',
            'boost_locale'
        ]
        return (home, sys_includes, sys_libdirs, libs)

    def finalize_options(self):
        build_ext.finalize_options(self)

        pEpLog("local: ", self.local)
        pEpLog("prefix: ", self.prefix)
        pEpLog("sys.platform: ", sys.platform)

        # get build information for platform
        if sys.platform == 'winnt':
            build_info = self.get_build_info_winnt()
        elif sys.platform == 'darwin':
            build_info = self.get_build_info_darwin()
        elif sys.platform == 'linux':
            build_info = self.get_build_info_linux()
        else:
            pEpLog("Platform not supported:" + sys.platform)
            exit()

        (home, sys_includes, sys_libdirs, libs) = build_info

        # Build the Includes -I and Library paths -L
        # Start empty
        includes = []
        libdirs = []

        # Append home-dir
        if self.local:
            pEpLog("local mode")
            home_include = [join(home, 'include')]
            home_libdirs = [join(home, 'lib')]
            includes += home_include
            libdirs += home_libdirs

        # Append prefix-dir
        if self.prefix:
            prefix_include = [join(self.prefix, 'include')]
            prefix_libdirs = [join(self.prefix, 'lib')]
            includes += prefix_include
            libdirs += prefix_libdirs

        # Append default system dirs
        includes += sys_includes
        libdirs += sys_libdirs

        # Compile flags
        compile_flags = ['-std=c++14', '-fpermissive']
        if self.debug:
            pEpLog("debug mode")
            compile_flags += ['-O0', '-g', '-UNDEBUG']

        # Apply the build information
        global module_pEp
        module_pEp.include_dirs = includes
        module_pEp.library_dirs = libdirs
        module_pEp.libraries = libs
        module_pEp.extra_compile_args = compile_flags

        pEpLog("Include Dirs:", module_pEp.include_dirs)
        pEpLog("Libs Dirs:", module_pEp.library_dirs)
        pEpLog("Libraries:", module_pEp.libraries)
        pEpLog("Compile flags:", module_pEp.extra_compile_args)

    def run(self):
        build_ext.run(self)


if sys.platform == 'winnt':
    if sys.version_info[0] >= 3:
        import winreg
    else:
        import _winreg as winreg

if sys.version_info[0] < 3:
    FileNotFoundError = EnvironmentError

module_pEp = Extension(
    'native_pEp',
    sources=[
        'src/pEp/native_pEp/pEpmodule.cc',
        'src/pEp/native_pEp/basic_api.cc',
        'src/pEp/native_pEp/identity.cc',
        'src/pEp/native_pEp/message.cc',
        'src/pEp/native_pEp/message_api.cc',
        'src/pEp/native_pEp/str_attr.cc',
        # 'src/pEp/native_pEp/user_interface.cc',
    ],
)

# "MAIN" Function
setup(
    name='pEp',
    version='2.1.0-RC2',
    description='p≡p for Python',
    author="Volker Birk",
    author_email="vb@pep-project.org",
    maintainer="Heck",
    maintainer_email="heck@pep.foundation",
    package_dir={'': 'src'},
    packages=['pEp'],
    ext_modules=[module_pEp],
    cmdclass={
        'build_ext': BuildExtCommand,
    },
)
