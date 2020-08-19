PREFIX = /home/heck/local-default/
DEBUG = 0
BUILD_DIR = ./build

BUILD_EXT_OPTS = --prefix=$(PREFIX)

ifeq ($(DEBUG),1)
	BUILD_EXT_OPTS+=--debug
endif

.PHONY: all build clean

all: build_ext

build_ext:
	python3 setup.py build_ext $(BUILD_EXT_OPTS)

clean:
	rm -r $(BUILD_DIR)