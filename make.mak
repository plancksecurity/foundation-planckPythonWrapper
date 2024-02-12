# build dirs
BUILD_DIR = $(ProjectDir)..\build
DIST_DIR = $(ProjectDir)..\dist
PYTHON_PROC = $(PREFIX)\vcpkg\installed\x64-windows\tools\python3\python.exe

# create wheel and egg package in dist
dist: dist-whl dist-egg

# create wheel package in dist
dist-whl: compile
    CD ..
    $(PYTHON_PROC) setup.py bdist_wheel

# create egg package in dist
dist-egg: compile
    CD ..
    $(PYTHON_PROC) setup.py bdist_egg

# build the module into build
compile:
    CD ..
    $(PYTHON_PROC) setup.py build_ext --debug --prefix=$(PREFIX)

# delete output directories
clean:
    @if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
    @if exist $(DIST_DIR) rmdir /S /Q $(DIST_DIR)

# create directories and build application
all: clean dist

# release build
release: clean
    CD ..
    CP $(PREFIX)\vcpkg\installed\x64-windows-static-md\debug\lib\python311_d.lib  python311.lib
    $(PYTHON_PROC) setup.py build_ext --OutDir=$(OUTDIR) --prefix=$(PREFIX)
    $(PYTHON_PROC) setup.py bdist_wheel --OutDir=$(OUTDIR)

#debug build
debug: clean
    CD ..
    CP $(PREFIX)\vcpkg\installed\x64-windows-static-md\lib\python311.lib python311.lib
    $(PYTHON_PROC) setup.py build_ext --debug --OutDir=$(OUTDIR) --prefix=$(PREFIX)
    $(PYTHON_PROC) setup.py bdist_wheel --OutDir=$(OUTDIR)
