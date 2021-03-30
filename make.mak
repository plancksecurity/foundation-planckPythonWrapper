# build dirs
BUILD_DIR = $(ProjectDir)..\build
DIST_DIR = $(ProjectDir)..\dist

# create wheel and egg package in dist
dist: dist-whl dist-egg

# create wheel package in dist
dist-whl: compile
    PY -3.8-32 setup.py bdist_wheel

# create egg package in dist
dist-egg: compile
    PY -3.8-32 setup.py bdist_egg

# build the module into build
compile:
    CD..
    PY -3.8-32 setup.py build_ext --debug

# delete output directories
clean:
    @if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
    @if exist $(DIST_DIR) rmdir /S /Q $(DIST_DIR)

# create directories and build application
all: clean dist

# release build
release: clean
    CD..
    PY -3.8-32 setup.py build_ext
    PY -3.8-32 setup.py bdist_wheel

#debug build
debug: clean
    CD..
    PY -3.8-32 setup.py build_ext --debug
    PY -3.8-32 setup.py bdist_wheel