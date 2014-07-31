CC = gcc --std=c99
CPPFLAGS = -I/tgac/software/production/samtools/0.1.18/x86_64/include
CFLAGS = -pedantic -Wall -O2 -g
LDFLAGS = -L/tgac/software/production/samtools/0.1.18/x86_64/lib
LDLIBS = -pthread -lbam -lz

PROGS = bambaseatpos

all: $(PROGS)

clean:
	rm -f $(PROGS)
