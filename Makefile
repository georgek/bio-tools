CC ?= gcc --std=c99
CPPFLAGS += -I$(HOME)/include
CFLAGS += -pedantic -Wall -O2 -g
LDFLAGS += -L$(HOME)/lib
LDLIBS += -pthread -lz -lhts
SAMTOOLSDIR ?= $(HOME)/src/samtools
CXXFLAGS += -std=c++11 -O2

PROGS = bambaseatpos resample pileupcvg consensus average int-count int-hist fastq-subsample

all: $(PROGS)

clean:
	rm -f $(PROGS)
