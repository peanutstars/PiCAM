
ifndef	BASEDIR
BASEDIR		:=$(shell pwd)/..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

SCRIPT_FILES	:=	picam

INSTALLDIR		:=$(TARGETDIR)/system/bin

all:

clean:

install: all
	@install -d $(INSTALLDIR)
	@cp -a $(SCRIPT_FILES) $(INSTALLDIR)


#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common
