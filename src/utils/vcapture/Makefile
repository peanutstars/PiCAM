#
#------------------------------------------------------------------------------

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

TARGET			:= vcapture
OBJS			:= capture.o

INSTALLDIR		:=$(TARGETDIR)/system/bin

EXTRA_LDFLAGS	+=-lpthread
EXTRA_LDFLAGS	+=-lrt

#------------------------------------------------------------------------------

include $(BASEDIR)/build/Rules.common
