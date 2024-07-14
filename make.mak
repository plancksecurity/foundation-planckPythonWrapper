# build dirs
BUILD_DIR = $(ProjectDir)..\build
DIST_DIR = $(ProjectDir)..\dist
PYTHON_PROC = $(PREFIX)\vcpkg\installed\$(TARGET)-windows\tools\python3\python.exe

# create wheel and egg package in dist
dist: dist-whl dist-egg

# create wheel package in dist
dist-whl: compile
    CD ..
    ECHO Target: $(TARGET)
    $(PYTHON_PROC) setup.py bdist_wheel --target=$(TARGET)

# create egg package in dist
dist-egg: compile
    CD ..
    ECHO Target: $(TARGET)
    $(PYTHON_PROC) setup.py bdist_egg --target=$(TARGET)

# build the module into build
compile:
    CD ..
    ECHO Target: $(TARGET)
    $(PYTHON_PROC) setup.py build_ext --debug --prefix=$(PREFIX) --target=$(TARGET)

# delete output directories
clean:
    @if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
    @if exist $(DIST_DIR) rmdir /S /Q $(DIST_DIR)

# create directories and build application
all: clean dist

#COPY $(PREFIX)\vcpkg\installed\$(TARGET)-windows\debug\lib\python311_d.lib  python311.lib /y
#COPY $(PREFIX)\vcpkg\installed\$(TARGET)-windows\lib\python311.lib python311.lib /y

# release build
release: clean
    CD ..
    ECHO Target: $(TARGET)
    $(PYTHON_PROC) setup.py build_ext --OutDir=$(OUTDIR) --prefix=$(PREFIX) --target=$(TARGET)
    $(PYTHON_PROC) setup.py bdist_wheel --OutDir=$(OUTDIR) --target=$(TARGET)

#debug build
debug: clean
    CD ..
    ECHO Target: $(TARGET)
    $(PYTHON_PROC) setup.py build_ext --debug --OutDir=$(OUTDIR) --prefix=$(PREFIX) --target=$(TARGET)
    $(PYTHON_PROC) setup.py bdist_wheel --OutDir=$(OUTDIR) --target=$(TARGET)

