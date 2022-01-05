include Makefile.conf
TARGET=$(TARGET_PEP)

# Specific Build settings
#CXXFLAGS+=-Wno-unused-result -Wsign-compare -Wunreachable-code -fno-common -dynamic -g -fwrapv -O3 -Wall -pipe -Os -isysroot/Library/Developer/CommandLineTools/SDKs/MacOSX10.14.sdk
CXXFLAGS+=$(shell python-config --cflags)
#INCLUDES+=$(shell python-config --includes)
INCLUDES+=-I/opt/local/include
LIB_DIRS+=-L$(shell python-config --prefix)
LIB_DIRS+=-L/opt/local/lib
LIBS+=-lboost_python3-mt -lboost_locale-mt
LDFLAGS+=$(shell python-config --ldflags)



# Combine Settings
CXXFLAGS+=$(INCLUDES)
LDFLAGS+=$(LIB_DIRS)
LDFLAGS+=$(LIBS)

SRCS:=$(wildcard *.cc)
OBJS:=$(SRCS:.cc=.o)

.PHONY: clean

all: $(TARGET)

# Using implicit compile target
# And explicit link taget
$(TARGET): $(OBJS)
#	$(CXX) $(LDFLAGS) -o $@ $^

clean:
	rm -rf $(TARGET)
	rm -rf $(OBJS)
