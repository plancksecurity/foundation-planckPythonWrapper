include Makefile.conf

.PHONY: all dist dist-egg dist-whl install install-prefix install-sys compile clean devenv envtest docs clean-docs

all: dist

# Build
# =====
compile:
	python3 setup.py build_ext $(DEBUG_OPT) $(PREFIX_OPT)

# Packaging
# =========
# create wheel and egg package in dist/
dist: dist-whl dist-egg

# create wheel package in dist/
dist-whl: compile
	python3 setup.py bdist_wheel

# create egg package in dist/
dist-egg: compile
	python3 setup.py bdist_egg

# Installation
# ============
# installs the package system wide
install: compile
	python3 setup.py install --force

# installs the package into your user home
install-user: compile
	python3 setup.py install --force --user


clean: clean-docs
	rm -r $(BUILD_DIR)
	rm -r $(DIST_DIR)

# Creates an ad-hoc dev env using the compiled module
devenv:
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	DYLD_LIBRARY_PATH=$(PREFIX)/lib \
	PYTHONPATH=`pwd`/build/lib.linux-x86_64-3.7:`pwd`/build/lib.macosx-10.9-x86_64-3.8: \
	bash -l

# Tests if the current environment is able to load the pEp module
envtest:
	python3 -c 'import pEp'


# Documentation
# =============
docs:
	make html -C docs/

clean-docs
	make clean -C docs/
