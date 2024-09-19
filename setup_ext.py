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

def get_build_info_win32(debug, target, outDir):
    home = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
    inst_prefix = windowsGetInstallLocation(outDir)
    sys_includes = [
        join(home, "vcpkg", "installed", target+"-windows","include")
    ]
    sys_libdirs = [ join(inst_prefix, 'Debug')] if debug else [ join(inst_prefix, 'Release')]
    libs = [
        'user32',
        'shell32',
        'kernel32',
        'Advapi32',
        'libpEpAdapter',
        'libpEpCxx11',
        'pEpEngine',
        'archive',
        'charset',
        'cryptopp',
        'iconv',
        'libcrypto',
        'libssl',
        'libxml2',
        'lzma',
    ]

    debug_libs = [
        'bz2d',
        'libexpatd',
        'lz4d',
        'zlibd',
        'zstd',
        'python311_d',
    ]

    ndebug_libs = [
        'bz2',
        'libexpat',
        'lz4',
        'zlib',
        'zstd',
        'python311',
    ]

    if debug:
        libs=libs+debug_libs
        vcpk_libs=join(home, "vcpkg", "installed", target+"-windows","debug","lib")
        sys_libdirs.append(vcpk_libs)
    else:
        libs=libs+ndebug_libs
        vcpk_libs=join(home, "vcpkg", "installed", target+"-windows","lib")
        sys_libdirs.append(vcpk_libs)

    for fn in os.listdir(vcpk_libs):
        if "boost_" in fn:
            l=fn.replace(".lib","")
            libs.append(l)

    compile_flags = ['/std:c++14', '/permissive','/D_WIN32_WINNT=0x0A00', '/INCREMENTAL:YES']
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

def get_build_info(debug, target, outDir):
    """ get build information for platform"""
    build_info = None
    if sys.platform == 'win32':
        build_info = get_build_info_win32(debug, target, outDir)
    elif sys.platform == 'darwin':
        build_info = get_build_info_darwin(debug)
    elif sys.platform == 'linux':
        build_info = get_build_info_linux(debug)
    else:
        pEpLog("Platform not supported:" + sys.platform)

    return build_info
