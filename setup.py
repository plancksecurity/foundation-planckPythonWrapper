# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt
#
# For more debugging, export DISTUTILS_DEBUG=True

from __future__ import print_function

import sys
from os.path import join
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel
from setup_ext import *
import distutils


class BuildExtCommand(build_ext):
    user_options = build_ext.user_options + [
        ('prefix=', None, 'Use pEp-base installation in prefix (libs/includes)'),
        ('OutDir=', None, 'Specifies a path to the output wrapper solution directory.'),
    ]

    def initialize_options(self):
        super().initialize_options()
        build_ext.initialize_options(self)
        self.prefix = getattr(self, "prefix=", None)
        if not hasattr(self, "OutDir") or self.OutDir is None:
            self.OutDir = getattr(self, "OutDir=", None)

    def find_boost_python(self, lib_dirs):
        boost_python_names = ["boost_python" + suffix for suffix in ["3", "38", "39", "310", "311"]]
        ccompiler = distutils.ccompiler.new_compiler()
        for boost in boost_python_names:
            found = ccompiler.find_library_file(lib_dirs, boost)
            if found is not None:
                return boost

    def finalize_options(self):
        build_ext.finalize_options(self)

        pEpLog("prefix: ", self.prefix)
        pEpLog("sys.platform: ", sys.platform)

        # Get build information for platform
        build_info = get_build_info(self.debug, self.OutDir)
        if build_info is None:
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

class CustomBdistWheel(bdist_wheel):
    user_options = bdist_wheel.user_options + [
        ('OutDir=', None, 'Specifies a path to the output wrapper solution directory.'),
    ]

    def initialize_options(self):
        super().initialize_options()
        bdist_wheel.initialize_options(self)
        self.debug = getattr(self, "debug=", False)
        self.OutDir = getattr(self, "OutDir=", None)

    def finalize_options(self):
        bdist_wheel.finalize_options(self)

        pEpLog("sys.platform: ", sys.platform)

        # Get build information for platform
        build_info = get_build_info(self.debug, self.OutDir)
        if build_info is None:
            exit()

    def run(self):
        # Pass the value of OutDir to the build_ext command
        self.distribution.get_command_obj('build_ext').OutDir = self.OutDir
        self.run_command('build_ext')
        super().run()

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
        'bdist_wheel': CustomBdistWheel,
    },
    # While not using a pyproject.toml, support setuptools_scm setup.cfg usage,
    # see https://github.com/pypa/setuptools_scm/#setupcfg-usage
    use_scm_version={
        'tag_regex': r'^(?P<prefix>planck_v)?(?P<version>[vV]?\d+\.\d+\.\d+[^+]*)\+?(?P<dirty>.*)?$',
        'write_to': 'src/pEp/__version__.py',
        #TODO: fallback_version does not seem to work in case os missing tag
        'fallback_version' : '0.0.0-RC0'
    }
)
