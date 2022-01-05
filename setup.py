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
        ('prefix=', None, 'Use pEp-base installation in prefix (libs/includes)'),
    ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.prefix = getattr(self, "prefix=", None)

    def windowsGetInstallLocation(self):
        reg_path = "SOFTWARE\\Classes\\TypeLib\\{564A4350-419E-47F1-B0DF-6FCCF0CD0BBC}\\1.0\\0\\win32"
        KeyName = None
        regKey = None
        pEpLog("Registry Lookup:", reg_path, KeyName)
        try:
            regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
            # Keys: Description, FileName, FriendlyName, LoadBehavior
            com_server, _ = winreg.QueryValueEx(regKey, KeyName)
        except WindowsError as error:
            pEpLog("Error ocurred: " + error)
            com_server = None
        finally:
            if winreg:
                winreg.CloseKey(regKey)
        dirname = os.path.dirname
        ret = dirname(dirname(com_server))
        pEpLog("Value:", ret)
        return ret

    def windowsGetBoostDirs(self):
        for dir in [f.path for f in os.scandir(join(os.getcwd(), 'build-windows', 'packages')) if f.is_dir()]:
            if 'boost.' in dir or 'boost_python' in dir or 'boost_locale' in dir:
                yield join(dir, 'lib', 'native'), join(dir, 'lib', 'native', 'include')

    def get_build_info_win32(self):
        home = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
        inst_prefix = self.windowsGetInstallLocation()
        sys_includes = [
            join(inst_prefix),
        ] + [d[1] for d in self.windowsGetBoostDirs()]
        sys_libdirs = [ join(inst_prefix, 'Debug')] if self.debug else [ join(inst_prefix, 'Release')]
        sys_libdirs += [d[0] for d in self.windowsGetBoostDirs()]
        libs = [
            'pEpEngine',
            'libpEpAdapter',
            'boost_python38-vc142-mt-x32-1_72',
            'boost_locale-vc142-mt-x32-1_72'
        ]
        compile_flags = ['/std:c++14', '/permissive']
        if self.debug:
            pEpLog("debug mode")
            compile_flags += ['/Od', '/Zi', '/DEBUG']

        return (home, sys_includes, sys_libdirs, libs, compile_flags)


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
            'boost_python3-mt',
            'boost_locale-mt'
        ]
        compile_flags = ['-std=c++14', '-fpermissive']
        if self.debug:
            pEpLog("debug mode")
            compile_flags += ['-O0', '-g', '-UNDEBUG']

        return (home, sys_includes, sys_libdirs, libs, compile_flags)


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
        compile_flags = ['-std=c++14', '-fpermissive']
        if self.debug:
            pEpLog("debug mode")
            compile_flags += ['-O0', '-g', '-UNDEBUG']

        return (home, sys_includes, sys_libdirs, libs, compile_flags)


    def finalize_options(self):
        build_ext.finalize_options(self)

        pEpLog("prefix: ", self.prefix)
        pEpLog("sys.platform: ", sys.platform)


        # get build information for platform
        if sys.platform == 'win32':
            build_info = self.get_build_info_win32()
        elif sys.platform == 'darwin':
            build_info = self.get_build_info_darwin()
        elif sys.platform == 'linux':
            build_info = self.get_build_info_linux()
        else:
            pEpLog("Platform not supported:" + sys.platform)
            exit()

        (home, sys_includes, sys_libdirs, libs, compile_flags) = build_info

        # Build the Includes -I and Library paths -L
        # Start empty
        includes = []
        libdirs = []


        # Append prefix-dir
        if self.prefix:
            prefix_include = [join(self.prefix, 'include')]
            prefix_libdirs = [join(self.prefix, 'lib')]
            includes += prefix_include
            libdirs += prefix_libdirs

        # Append default system dirs
        includes += sys_includes
        libdirs += sys_libdirs

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


if sys.platform == 'win32':
    if sys.version_info[0] >= 3:
        import winreg
    else:
        import _winreg as winreg

if sys.version_info[0] < 3:
    FileNotFoundError = EnvironmentError

module_pEp = Extension(
    'pEp._pEp',
    sources=[
        'src/pEp/_pEp/pEpmodule.cc',
        'src/pEp/_pEp/basic_api.cc',
        'src/pEp/_pEp/identity.cc',
        'src/pEp/_pEp/message.cc',
        'src/pEp/_pEp/message_api.cc',
        'src/pEp/_pEp/str_attr.cc',
    ],
)

# "MAIN" Function
setup(
    package_dir={'': 'src'},
    packages=['pEp'],
    ext_modules=[module_pEp],
    cmdclass={
        'build_ext': BuildExtCommand,
    },
    # While not using a pyproject.toml, support setuptools_scm setup.cfg usage,
    # see https://github.com/pypa/setuptools_scm/#setupcfg-usage
    use_scm_version={
        'write_to': 'src/pEp/__version__.py',
        #TODO: fallback_version does not seem to work in case os missing tag
        'fallback_version' : '0.0.0-RC0'
    }
)
