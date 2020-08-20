PREFIX = /home/heck/local-default/
DEBUG = 1
BUILD_DIR = ./build

BUILD_EXT_OPTS = --prefix=$(PREFIX)

ifeq ($(DEBUG),1)
	BUILD_EXT_OPTS+=--debug
endif

.PHONY: all build clean devenv envtest

all: build_ext

build_ext:
	python3 setup.py build_ext $(BUILD_EXT_OPTS)

clean:
	rm -r $(BUILD_DIR)

devenv:
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	PYTHONPATH=`pwd`/build/lib.linux-x86_64-3.7:\
	`pwd`/src \
	bash -l

envtest:
	python3 -c 'import pEp'