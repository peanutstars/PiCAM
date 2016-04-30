
ifndef	BASEDIR
BASEDIR		:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

SCRIPT_FILES	:= 

INSTALLDIR		:=$(TBINDIR)

all:

clean:

install: all
	@install -d $(INSTALLDIR)
	@install $(SCRIPT_FILES) $(INSTALLDIR)


#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common
