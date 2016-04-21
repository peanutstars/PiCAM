#
SRCDIR		:= src

ifndef	BASEDIR
BASEDIR			:=$(shell pwd)/$(SRCDIR)
endif
include $(BASEDIR)/Rules.mk

all:
	$(MAKE) -C $(SRCDIR)

clean:
	$(MAKE) -C $(SRCDIR) clean

install:
	$(MAKE) -C $(SRCDIR) install
