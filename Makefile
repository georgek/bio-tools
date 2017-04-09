CC = gcc --std=c99
CPPFLAGS += -I$(HOME)/include
CFLAGS += -ansi -pedantic -Wall -O2 -g
LDFLAGS += -L$(HOME)/lib
CXXFLAGS += -std=c++11 -O2

PROGS = bambaseatpos resample pileupcvg consensus average int-count int-hist fastq-subsample soap-fix

all: $(PROGS)

clean:
	rm -f $(PROGS)
