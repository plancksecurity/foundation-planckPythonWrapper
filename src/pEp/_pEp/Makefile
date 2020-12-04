TARGET=_pEp.so
CXX=g++

# Include dirs
INCLUDES=-I/Users/heck/local-default/include
INCLUDES+=-I/opt/local/Library/Frameworks/Python.framework/Versions/3.8/include/python3.8

# Libs
LIB_DIRS=-L/opt/local/lib -L/Users/heck/local-default/lib
LIBS=-lpEpEngine -lpEpAdapter -lboost_python38-mt -lboost_locale-mt

# Compile
CXXFLAGS+=-std=c++11 -Wno-unused-result -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3 -Wall -pipe -Os -isysroot/Library/Developer/CommandLineTools/SDKs/MacOSX10.14.sdk
CXXFLAGS+=$(INCLUDES)

# Link
LDFLAGS+= -undefined dynamic_lookup
LDFLAGS+=$(LIB_DIRS)
LDFLAGS+=$(LIBS)

SRCS				:= $(wildcard *.cc)
OBJS				:= $(SRCS:.cc=.o)

.PHONY: clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

clean:
	rm -rf $(TARGET)
	rm -rf $(OBJS)
