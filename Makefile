CC ?= gcc --std=c99
CPPFLAGS += -I$(HOME)/include
CFLAGS += -pedantic -Wall -O2 -g
LDFLAGS += -L$(HOME)/lib
LDLIBS += -pthread -lz -lhts
SAMTOOLSDIR ?= $(HOME)/src/samtools

PROGS = bambaseatpos resample pileupcvg

all: $(PROGS)

bamvcftool: bamvcftool.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -I$(SAMTOOLSDIR) $(LDFLAGS) -o bamvcftool bamvcftool.c $(SAMTOOLSDIR)/libbam.a $(LDLIBS)

clean:
	rm -f $(PROGS)
