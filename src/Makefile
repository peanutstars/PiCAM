#
#------------------------------------------------------------------------------

ifndef	BASEDIR
BASEDIR			:=$(shell pwd)
endif
WHOAMI			:=$(shell whoami)
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

SUBDIRS			:= \
					utils
						
#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common

remove-target:
	@rm -rf $(PF_OUTPUT_DIR)
