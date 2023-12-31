include Makefile.conf

.PHONY: all compile compile-inplace dist dist-egg dist-whl install install-user venv envtest install-test test develop docs  clean clean-all clean-docs
all: install

# Build
# =====
compile:
	python3 setup.py build_ext $(DEBUG_OPT) $(PREFIX_OPT)

compile-inplace:
	python3 setup.py build_ext $(DEBUG_OPT) $(PREFIX_OPT) --inplace

makefile-build:
	$(MAKE) -C src/pEp/_pEp/

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


# Envrionment
# ===========
# Creates and activates a new venv that has the LD_LIBRARY_PATH/DYLD_LIBRARY_PATH
# already set for the prefix specified in local.conf
# Only activates venv if already existing
venv:
	python3 -m venv $(VENV_DIR)
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	DYLD_LIBRARY_PATH=$(PREFIX)/lib \
	bash --rcfile $(VENV_DIR)/bin/activate

# Tests if the current environment is able to load the pEp module
envtest:
	HOME=. python3 -c 'import pEp'

# Test
# ====
# Use these targets only in venv created with 'make venv'
install-test: compile
	pip3 install .[test]

test:
	pytest tests


# Development
develop: compile
	pip install -e .


# Documentation
# =============
docs: compile-inplace
	make html -C docs/


# Housekeeping
# ============
clean-all: clean clean-docs
	rm -rf $(VENV_DIR)

clean: clean-makefile-build
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf $(PYTHON_ARTIFACTS)
	rm -rf $(VERSION_FILE)
	rm -rf $(BUILD_INPLACE)

clean-docs:
	make clean -C docs/

clean-makefile-build:
	$(MAKE) -C src/pEp/_pEp clean
