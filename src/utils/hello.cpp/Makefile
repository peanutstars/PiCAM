#
#------------------------------------------------------------------------------

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

CXXTARGET		:= hellocpp
OBJS			:= hello.o

INSTALLDIR		:=$(TARGETDIR)/system/bin

EXTRA_CPPFLAGS  += -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64

EXTRA_LDFLAGS	+=-lpthread
EXTRA_LDFLAGS	+=-lrt

#------------------------------------------------------------------------------

include $(BASEDIR)/build/Rules.common
