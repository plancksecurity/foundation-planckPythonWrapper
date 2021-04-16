import os
import re
import sys
import subprocess
import winreg
import zipfile as zf
from os.path import dirname
from os.path import join

def get_bindependencies(lib, debug=False):
    """Gets the pEp dependencies of a library"""

    python_location = sys.exec_prefix
    bindepend = join(python_location, 'Scripts', 'pyi-bindepend.exe')
    output = subprocess.run([bindepend, lib], capture_output=True)
    if os.path.isfile(lib):
        yield lib
    if len(output.stdout) > 0:
        deps = parse_bindepend_output(output.stdout)
        for dep in add_full_paths(deps, debug):
            for d in get_bindependencies(dep):
                yield d


def parse_bindepend_output(stdout):
    """Parses the output of pyi-bindepent and returns a list of file names"""
    
    deps = []
    if stdout == None:
        return None
    p = re.compile('(.*){(.*)}(.*)')
    str_val = bytes.decode(stdout)
    raw_val = p.findall(str_val)
    if len(raw_val) == 0:
        return deps
    else:
        libs = raw_val[0][1].replace(' ', '').split(',')
        for lib in libs:
            lib = lib.strip("'")
            if not 'api' in lib:
                deps.append(lib)
    return deps    


def get_pEp_install_location(debug=False):
    """Gets the location where pEp is installed"""

    reg_path = "SOFTWARE\\Classes\\TypeLib\\{564A4350-419E-47F1-B0DF-6FCCF0CD0BBC}\\1.0\\0\\win32"
    KeyName = None
    regKey = None
    try:
        regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        # Keys: Description, FileName, FriendlyName, LoadBehavior
        com_server, _ = winreg.QueryValueEx(regKey, KeyName)
    except WindowsError as error:
        print('Error getting install location: ' + error)
        com_server = None
    finally:
        if winreg:
            winreg.CloseKey(regKey)
    location = os.path.dirname(com_server)
    if debug:
        location = location.strip('Release') + 'Debug'
    return location


def get_boost_directories():
    """Gets the location of the boost libraries"""
    
    for dir in [f.path for f in os.scandir(join(os.getcwd(), 'build-windows', 'packages')) if f.is_dir()]:
        if 'boost.' in dir or 'boost_python' in dir or 'boost_locale' in dir:
            yield join(dir, 'lib', 'native')    


def add_full_paths(libs, debug=False):
    """Combines a list of libraries with a set of common directories. Returns a list of file names that exist on this machine"""
    
    paths = [get_pEp_install_location(debug)] + [dir for dir in get_boost_directories()] + [p for p in os.environ['PATH'].split(';')]
    paths = [p for p in paths if not "system32" in p.lower()]
    full_paths = [] 
    for lib in libs:
        for p in paths:
            test_path = join(p, lib)
            if os.path.isfile(test_path) and not test_path.casefold() in (f.casefold for f in full_paths):
                full_paths.append(test_path)
    return full_paths


def main():  
    
    args = sys.argv
    cwd = dirname(args[0])
    del args[0]

    # Check for debug build
    debug = False
    if len(args) > 0 and args[0] == '--debug':
        debug = True
        del args[0]

    # Get the pEp wheel and extract the pEp Python library
    dist_path = join(dirname(cwd), 'dist')
    print('Dist path is: ' + dist_path)
    pEp_python_library = None
    if os.path.exists(dist_path):
        for _, _, files in os.walk(dist_path):
            for f in files:
                if f[:3] == 'pEp' and f[-3:] == 'whl':
                    wheel_name = join(dist_path, f)
                    with zf.ZipFile(wheel_name, 'a') as wheel:
                        for archive_member in wheel.namelist():
                            if '_pEp' in archive_member and archive_member[-3:] == 'pyd':
                                wheel.extract(archive_member, path=dist_path)                            
                                pEp_python_library = join(dist_path, archive_member)
                                print('pEp Python library found and extracted to ' + pEp_python_library)
                                break
                    break

    # Get all dependencies for the pEp Python library
    if pEp_python_library == None:
        raise FileNotFoundError('pEp Python library not found in ' + dist_path)
    pEp_python_library = pEp_python_library.replace('/', '\\')
    libs = []
    for lib in get_bindependencies(pEp_python_library, debug):
        if not lib.casefold() in (l.casefold for l in libs) and lib.casefold() != pEp_python_library.casefold():
            print('Dependency found: ' + lib)
            libs.append(lib)

    # Copy dependencies into the wheel
    with zf.ZipFile(wheel_name, 'a') as wheel:
        for lib in libs:
            filename = os.path.basename(lib)
            arcname = 'pEp/' + filename
            if not arcname in wheel.namelist():
                wheel.write(filename=lib, arcname=arcname, compress_type=zf.ZIP_DEFLATED)

    # Delete the temporarily extracted pEp Python library
    if os.path.isfile(pEp_python_library):
        os.remove(pEp_python_library)
        dir = os.path.dirname(pEp_python_library)
        d = dir[-3:]
        if dir[-3:].lower() == 'pep' and os.path.isdir(dir):
            os.rmdir(dir)


if __name__ == '__main__':
    main()