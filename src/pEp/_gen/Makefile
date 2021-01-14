include Makefile.conf

TARGET=_gen.so

TARGET_MODULE_DYN=$(TARGET)
TARGET_MODULE_STATIC=$(TARGET)

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

.PHONY: all gen module_dyn module_static clean

all: static

static: gen module_static

dyn: gen module_dyn

gen:
	$(MAKE) -C gen

module_dyn: $(TARGET_MODULE_DYN)

$(TARGET_MODULE_DYN) : $(OBJS)
	$(CXX) $(LDFLAGS_DYN) -o $@ $^

module_static: $(TARGET_MODULE_STATIC)

$(TARGET_MODULE_STATIC) : $(OBJS) $(LIBS_STATIC)
	$(CXX) $(LDFLAGS_STATIC) -o $@ $^

clean:
	$(MAKE) -C gen clean
	rm -f $(TARGET)
	rm -f $(OBJS)
