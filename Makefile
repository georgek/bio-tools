CC = gcc --std=c99
CPPFLAGS = -I$(HOME)/include
CFLAGS = -pedantic -Wall -O2 -g
LDFLAGS = -L$(HOME)/lib
LDLIBS = -pthread -lsqlite3 -lbam -lz

PROGS = pileupcvg resample

all: $(PROGS)

clean:
	rm -f $(PROGS)
