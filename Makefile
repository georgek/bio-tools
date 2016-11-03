CC ?= gcc --std=c99
CPPFLAGS += -I$(HOME)/include
CFLAGS += -pedantic -Wall -O2 -g
LDFLAGS += -L$(HOME)/lib
LDLIBS += -pthread -lz -lhts
SAMTOOLSDIR ?= $(HOME)/src/samtools

PROGS = bambaseatpos resample pileupcvg consensus average int-count

all: $(PROGS)

clean:
	rm -f $(PROGS)
