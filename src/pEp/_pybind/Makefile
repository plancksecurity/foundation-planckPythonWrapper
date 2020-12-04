include ../Makefile.conf
TARGET=$(TARGET_PYBIND)

# Specific Build settings
CXXFLAGS+=
INCLUDES+=
LIB_DIRS+=
LIBS+=
LDFLAGS+=



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
	$(CXX) $(LDFLAGS) -o $@ $^

clean:
	rm -rf $(TARGET)
	rm -rf $(OBJS)
