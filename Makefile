include Makefile.conf

.PHONY: all build clean devenv envtest

all: build_ext

build_ext:
	python3 setup.py build_ext $(BUILD_EXT_OPTS)

clean:
	rm -r $(BUILD_DIR)

devenv:
	LD_LIBRARY_PATH=$(PREFIX)/lib \
	DYLD_LIBRARY_PATH=$(PREFIX)/lib \
	PYTHONPATH=$PYTHONPATH:`pwd`/build/lib.linux-x86_64-3.7:\
	PYTHONPATH=$PYTHONPATH:`pwd`/build/lib.macosx-10.9-x86_64-3.8:\
	`pwd`/src \
	bash -l

envtest:
	python3 -c 'import pEp'