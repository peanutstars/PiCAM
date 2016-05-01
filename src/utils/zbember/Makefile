
ifndef	BASEDIR
BASEDIR		:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

INSTALLDIR		:=$(TBINDIR)

TARGET			= zbember
TARGETFILE		= ./zbember/build/exe/zbember

#------------------------------------------------------------------------------

all:
	$(MAKE) -C $(TARGET) -j $(CORES)

clean:
	$(MAKE) -C $(TARGET) clean

install: all
	@install -d $(INSTALLDIR)
	@install $(TARGETFILE) $(INSTALLDIR)
	
