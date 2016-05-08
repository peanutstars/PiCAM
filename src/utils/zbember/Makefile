
ifndef	BASEDIR
BASEDIR		:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

INSTALLDIR		:=$(TBINDIR)

TARGET			= zbember
TARGETFILE		= ./zbember/build/exe/zbember

-include Ember.mk
ifndef EMBER_BASE
EMBER_BASE		= /work/project/zigbee/EmberZNet5.4.2-GA
EMBER_APP_BASE	= $(EMBER_BASE)/app/builder/zbember
endif

export EMBER_APP_BASE

#------------------------------------------------------------------------------

all: initember
	@(if [ -e "$(EMBER_BASE)" ] ; then $(MAKE) -C $(TARGET) -j $(CORES); fi)

initember:
	@(if [ -e "$(EMBER_BASE)" ] ; then \
		[ ! -e "$(EMBER_APP_BASE)" ] && mkdir $(EMBER_APP_BASE); \
		cp -a $(TARGET)/* $(EMBER_APP_BASE); \
		if [ -e "$(EMBER_APP_BASE)/build" ] ; then rm -rf $(EMBER_APP_BASE)/build; fi; \
	fi)

clean:
	$(MAKE) -C $(TARGET) clean

install: all
	@install -d $(INSTALLDIR)
	@install $(TARGETFILE) $(INSTALLDIR)
	
