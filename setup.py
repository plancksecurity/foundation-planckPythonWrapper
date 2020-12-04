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

        global module_pybind11
        module_pybind11.include_dirs = includes
        module_pybind11.library_dirs = libdirs
        # module_pybind11.libraries = libs
        module_pybind11.extra_compile_args = compile_flags

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
    'pEp._pEp',
    sources=[
        'src/pEp/_pEp/adapter_main.cc',
        'src/pEp/_pEp/pEpmodule.cc',
        'src/pEp/_pEp/basic_api.cc',
        'src/pEp/_pEp/identity.cc',
        'src/pEp/_pEp/message.cc',
        'src/pEp/_pEp/message_api.cc',
        'src/pEp/_pEp/str_attr.cc',
        # 'src/pEp/_pEp/user_interface.cc',
    ],
)

module_pybind11 = Extension(
    'pEp._pybind',
    sources=[
        'src/pEp/_pybind/pEpmodule.cc',
    ],
)


# "MAIN" Function
setup(
    package_dir={'': 'src'},
    packages=['pEp'],
    ext_modules=[module_pEp, module_pybind11],
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
