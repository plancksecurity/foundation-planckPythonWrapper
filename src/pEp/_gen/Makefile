include Makefile.conf

TARGET=_gen.so

# Swap here, for static vs dyn linking
TARGET_MODULE_DYN=$(TARGET)
TARGET_MODULE_STATIC=

CXX=clang
CXXFLAGS+=-std=c++11 -g

SRCS+=$(wildcard *.cc)
OBJS+=$(SRCS:.cc=.o)

CXXFLAGS+=$(INCLUDES)
LDFLAGS_DYN+=-undefined dynamic_lookup $(LIBS_PATH) $(LIBS)
LDFLAGS_STATIC+=-undefined dynamic_lookup

$(info -----BUILD INFO----)
$(info SRCS 	$(SRCS))
$(info OBJS 	$(OBJS))

.PHONY: all gen gen-pybind module_dyn module_static clean

all: gen compile

gen:
	$(MAKE) -C gen

gen-pybind:
	$(MAKE) -C gen pybind

compile: $(TARGET)

$(TARGET_MODULE_DYN) : $(OBJS)
	$(CXX) $(LDFLAGS_DYN) -o $@ $^

$(TARGET_MODULE_STATIC) : $(OBJS) $(LIBS_STATIC)
	$(CXX) $(LDFLAGS_STATIC) -o $@ $^

clean:
	rm -f $(TARGET)
	rm -f $(OBJS)

clean-all: clean
	$(MAKE) -C gen clean
