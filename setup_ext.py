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

def get_build_info_win32(debug, outDir):
    home = environ.get('PER_USER_DIRECTORY') or environ.get('USERPROFILE')
    inst_prefix = windowsGetInstallLocation(outDir)
    sys_includes = [
        join(inst_prefix, "..", "vcpkg", "installed", "x64-windows","include")
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
    ]

    debug_libs = [
        'archive',
        'boost_atomic-vc140-mt-gd',
        'boost_chrono-vc140-mt-gd',
        'boost_cobalt-vc140-mt-gd',
        'boost_container-vc140-mt-gd',
        'boost_context-vc140-mt-gd',
        'boost_contract-vc140-mt-gd',
        'boost_coroutine-vc140-mt-gd',
        'boost_date_time-vc140-mt-gd',
        'boost_exception-vc140-mt-gd',
        'boost_fiber-vc140-mt-gd',
        'boost_filesystem-vc140-mt-gd',
        'boost_graph-vc140-mt-gd',
        'boost_iostreams-vc140-mt-gd',
        'boost_json-vc140-mt-gd',
        'boost_locale-vc140-mt-gd',
        'boost_log-vc140-mt-gd',
        'boost_log_setup-vc140-mt-gd',
        'boost_math_c99-vc140-mt-gd',
        'boost_math_c99f-vc140-mt-gd',
        'boost_math_c99l-vc140-mt-gd',
        'boost_math_tr1-vc140-mt-gd',
        'boost_math_tr1f-vc140-mt-gd',
        'boost_math_tr1l-vc140-mt-gd',
        'boost_nowide-vc140-mt-gd',
        'boost_program_options-vc140-mt-gd',
        'boost_python311-vc140-mt-gd',
        'boost_random-vc140-mt-gd',
        'boost_regex-vc140-mt-gd',
        'boost_serialization-vc140-mt-gd',
        'boost_stacktrace_noop-vc140-mt-gd',
        'boost_stacktrace_windbg-vc140-mt-gd',
        'boost_stacktrace_windbg_cached-vc140-mt-gd',
        'boost_system-vc140-mt-gd',
        'boost_thread-vc140-mt-gd',
        'boost_timer-vc140-mt-gd',
        'boost_type_erasure-vc140-mt-gd',
        'boost_unit_test_framework-vc140-mt-gd',
        'boost_url-vc140-mt-gd',
        'boost_wave-vc140-mt-gd',
        'boost_wserialization-vc140-mt-gd',
        'bz2d',
        'charset',
        'cryptopp',
        'iconv',
        'libcrypto',
        'libexpatd',
        'libssl',
        'libxml2',
        'lz4d',
        'lzma',
        'zlibd',
        'zstd',
        'python311_d',
    ]

    ndebug_libs = [
        'archive',
        'boost_atomic-vc140-mt',
        'boost_chrono-vc140-mt',
        'boost_cobalt-vc140-mt',
        'boost_container-vc140-mt',
        'boost_context-vc140-mt',
        'boost_contract-vc140-mt',
        'boost_coroutine-vc140-mt',
        'boost_date_time-vc140-mt',
        'boost_exception-vc140-mt',
        'boost_fiber-vc140-mt',
        'boost_filesystem-vc140-mt',
        'boost_graph-vc140-mt',
        'boost_iostreams-vc140-mt',
        'boost_json-vc140-mt',
        'boost_locale-vc140-mt',
        'boost_log-vc140-mt',
        'boost_log_setup-vc140-mt',
        'boost_math_c99-vc140-mt',
        'boost_math_c99f-vc140-mt',
        'boost_math_c99l-vc140-mt',
        'boost_math_tr1-vc140-mt',
        'boost_math_tr1f-vc140-mt',
        'boost_math_tr1l-vc140-mt',
        'boost_nowide-vc140-mt',
        'boost_program_options-vc140-mt',
        'boost_python311-vc140-mt',
        'boost_random-vc140-mt',
        'boost_regex-vc140-mt',
        'boost_serialization-vc140-mt',
        'boost_stacktrace_noop-vc140-mt',
        'boost_stacktrace_windbg-vc140-mt',
        'boost_stacktrace_windbg_cached-vc140-mt',
        'boost_system-vc140-mt',
        'boost_thread-vc140-mt',
        'boost_timer-vc140-mt',
        'boost_type_erasure-vc140-mt',
        'boost_unit_test_framework-vc140-mt',
        'boost_url-vc140-mt',
        'boost_wave-vc140-mt',
        'boost_wserialization-vc140-mt',
        'bz2',
        'charset',
        'cryptopp',
        'iconv',
        'libcrypto',
        'libexpat',
        'libssl',
        'libxml2',
        'lz4',
        'lzma',
        'zlib',
        'zstd',
        'python311',
    ]

    if debug:
        libs=libs+debug_libs
        sys_libdirs.append(join(inst_prefix, "..", "vcpkg", "installed", "x64-windows","debug","lib"))
    else:
        libs=libs+ndebug_libs
        sys_libdirs.append(join(inst_prefix, "..", "vcpkg", "installed", "x64-windows","lib"))

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
