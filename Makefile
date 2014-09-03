CC = gcc --std=c99
CPPFLAGS = -I$(HOME)/include
CFLAGS = -pedantic -Wall -O2 -g
LDFLAGS = -L$(HOME)/lib
LDLIBS = -pthread -lbam -lz

PROGS = bambaseatpos resample pileupcvg

all: $(PROGS)

clean:
	rm -f $(PROGS)
