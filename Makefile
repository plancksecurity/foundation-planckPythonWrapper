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
	pip3 install .

# installs the package into your user home
install-user: compile
	pip3 install . --user

clean: clean-docs
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf $(PYTHON_ARTIFACTS)
	rm -rf $(VERSION_FILE)
	rm -rf $(BUILD_INPLACE)


# Envrionment
# ===========
# Creates and activates a new venv that has the LD_LIBRARY_PATH/DYLD_LIBRARY_PATH
# already set for the prefix specified in local.conf
# Only activates venv if already existing
venv:
	python3 -m venv _venv
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	DYLD_LIBRARY_PATH=$(PREFIX)/lib \
	bash --rcfile _venv/bin/activate

# Tests if the current environment is able to load the pEp module
envtest:
	python3 -c 'import pEp'


# Documentation
# =============
docs:
	make html -C docs/

clean-docs:
	make clean -C docs/
