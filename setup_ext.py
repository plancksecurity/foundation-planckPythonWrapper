import os
from os import environ
from os.path import join
import platform
import sys

def pEpLog(*msg):
    import inspect
    msgstr = ''
    separator = ' '
    for m in msg:
        msgstr += str(m)
        msgstr += separator
    func = inspect.currentframe().f_back.f_code
    print(func.co_filename + " : " + func.co_name + " : " + msgstr)

def windowsGetInstallLocation(outDir):
    dirname = os.path.dirname
    ret = dirname(dirname(outDir))
    pEpLog("Value:", ret)
    return ret

def windowsGetBoostDirs():
    for dir in [f.path for f in os.scandir(join(os.getcwd(), 'build-windows', '..', '..', 'packages')) if f.is_dir()]:
        if 'boost.' in dir or 'boost_python' in dir or 'boost_locale' in dir:
            yield join(dir, 'lib', 'native'), join(dir, 'lib', 'native', 'include')

def get_build_info_win32(debug, outDir):
    home = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
    inst_prefix = windowsGetInstallLocation(outDir)
    sys_includes = [
        join(inst_prefix),
    ] + [d[1] for d in windowsGetBoostDirs()]
    sys_libdirs = [ join(inst_prefix, 'Debug')] if debug else [ join(inst_prefix, 'Release')]
    sys_libdirs += [d[0] for d in windowsGetBoostDirs()]
    libs = [
        'libpEpCxx11',
        'pEpEngine',
        'libpEpAdapter',
        'boost_python39-vc142-mt-x32-1_77',
        'boost_locale-vc142-mt-x32-1_77'
    ]
    compile_flags = ['/std:c++14', '/permissive']
    if debug:
        pEpLog("debug mode")
        compile_flags += ['/Od', '/Zi', '/DEBUG']

    return (home, sys_includes, sys_libdirs, libs, compile_flags)

def get_build_info_darwin(debug):
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
        'pEpCxx11',
        'boost_python3-mt',
        'boost_locale-mt'
    ]
    compile_flags = ['-std=c++14', '-fpermissive']
    if debug:
        pEpLog("debug mode")
        compile_flags += ['-O0', '-g', '-UNDEBUG']

    return (home, sys_includes, sys_libdirs, libs, compile_flags)

def get_build_info_linux(debug):
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
        'pEpCxx11',
        'boost_python3',
        'boost_locale',
        'z'
    ]
    compile_flags = ['-std=c++14', '-fpermissive']
    if debug:
        pEpLog("debug mode")
        compile_flags += ['-O0', '-g', '-UNDEBUG']

    return (home, sys_includes, sys_libdirs, libs, compile_flags)

def get_build_info(debug, outDir):
    """ get build information for platform"""
    build_info = None
    if sys.platform == 'win32':
        build_info = get_build_info_win32(debug, outDir)
    elif sys.platform == 'darwin':
        build_info = get_build_info_darwin(debug)
    elif sys.platform == 'linux':
        build_info = get_build_info_linux(debug)
    else:
        pEpLog("Platform not supported:" + sys.platform)

    return build_info
