#
#------------------------------------------------------------------------------

SCRIPTS	:=	initRPI.sh \
			initModule.sh \
			deinitModule.sh

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../src
endif
include $(BASEDIR)/Rules.mk

INSTALLDIR		:=$(TSCRIPTDIR)

#.PHONY: SCRIPTS

#------------------------------------------------------------------------------

install:
	@install -d $(INSTALLDIR)
	@install $(SCRIPTS) $(INSTALLDIR)

