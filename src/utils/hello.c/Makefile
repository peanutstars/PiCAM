#
#------------------------------------------------------------------------------

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

TARGET			:= helloc
OBJS			:= hello.o

INSTALLDIR		:=$(TARGETDIR)/system/bin

EXTRA_LDFLAGS	+=-lpthread
EXTRA_LDFLAGS	+=-lrt

#------------------------------------------------------------------------------

include $(BASEDIR)/build/Rules.common
