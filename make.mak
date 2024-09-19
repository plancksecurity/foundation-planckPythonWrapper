# build dirs
BUILD_DIR = $(ProjectDir)..\build
DIST_DIR = $(ProjectDir)..\dist
vcpkg_platform=x86-windows

!if "$(PROCESSOR_ARCHITECTURE)" == "AMD64"
vcpkg_platform=x64-windows
!endif

!if "$(PROCESSOR_ARCHITECTURE)" == "IA64"
vcpkg_platform=x64-windows
!endif

!if "$(PROCESSOR_ARCHITECTURE)" == "IA64"
vcpkg_platform=arm64-windows
!endif

!if "$(ROCESSOR_ARCHITEW6432)" == "AMD64"
vcpkg_platform=x64-windows
!endif

!if "$(ROCESSOR_ARCHITEW6432)" == "IA64"
vcpkg_platform=x64-windows
!endif

!if "$(ROCESSOR_ARCHITEW6432)" == "IA64"
vcpkg_platform=arm64-windows
!endif

PY=$(USERPROFILE)\vcpkg\installed\$(vcpkg_platform)\tools\python3\python.exe

# create wheel and egg package in dist
dist: dist-whl dist-egg

# create wheel package in dist
dist-whl: compile
    CD ..
    ECHO Target: $(TARGET)
    $(PY) setup.py bdist_wheel --target=$(TARGET)

# create egg package in dist
dist-egg: compile
    CD ..
    ECHO Target: $(TARGET)
    $(PY) setup.py bdist_egg --target=$(TARGET)

# build the module into build
compile:
    CD ..
    ECHO Target: $(TARGET)
    $(PY) setup.py build_ext --debug --prefix=$(PREFIX) --target=$(TARGET)

# delete output directories
clean:
    @if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
    @if exist $(DIST_DIR) rmdir /S /Q $(DIST_DIR)

# create directories and build application
all: clean dist

# release build
release: clean
    CD ..
    ECHO Target: $(TARGET)
    $(PY) setup.py build_ext --OutDir=$(OUTDIR) --prefix=$(PREFIX) --target=$(TARGET)
    $(PY) setup.py bdist_wheel --OutDir=$(OUTDIR) --target=$(TARGET)

#debug build
debug: clean
    CD ..
    ECHO Target: $(TARGET)
    $(PY) setup.py build_ext --debug --OutDir=$(OUTDIR) --prefix=$(PREFIX) --target=$(TARGET)
    $(PY) setup.py bdist_wheel --OutDir=$(OUTDIR) --target=$(TARGET)

