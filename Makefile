include Makefile.conf

.PHONY: all dist dist-egg dist-whl install install-prefix install-sys compile clean devenv envtest

all: dist

# create wheel and egg package in dist/
dist: dist-whl dist-egg

# create wheel package in dist/
dist-whl: compile
	python3 setup.py bdist_wheel

# create egg package in dist/
dist-egg: compile
	python3 setup.py bdist_egg


# installs the package into the user home
install: compile
	python3 setup.py install --force --user

# installs the package into PREFIX path
install-prefix: compile
	python3 setup.py install --force $(PREFIX_OPT)

# installs the package system wide
install-sys: compile
	python3 setup.py install --force


# build the module into build/
compile:
	python3 setup.py build_ext $(DEBUG_OPT) $(PREFIX_OPT)

clean:
	rm -r $(BUILD_DIR)
	rm -r $(DIST_DIR)

devenv:
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	DYLD_LIBRARY_PATH=$(PREFIX)/lib \
	PYTHONPATH=`pwd`/build/lib.linux-x86_64-3.7:`pwd`/build/lib.macosx-10.9-x86_64-3.8: \
	bash -l

envtest:
	python3 -c 'import pEp'
