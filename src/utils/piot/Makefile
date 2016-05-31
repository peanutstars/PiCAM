
ifndef	BASEDIR
BASEDIR		:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

SCRIPT_FILES	:= *.py *.sh config lpiot

INSTALLDIR		:=$(TBINDIR)

all:

clean:

install: all
	@install -d $(INSTALLDIR)
	@(cp -a $(SCRIPT_FILES) $(INSTALLDIR))
	@(find $(INSTALLDIR) -name "*.pyc" -exec rm {} \;)


#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common
