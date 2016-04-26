#
#------------------------------------------------------------------------------

SCRIPTS	:=	initRPI.sh \
			initModule.sh \
			deinitModule.sh

MAINSCRIPT	:= picam

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
	@install -d $(TUSRBIN)
	@install $(MAINSCRIPT) $(TUSRBIN)

