#
#------------------------------------------------------------------------------

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

TARGET			:= vcapture
OBJS			:= capture.o \
				   v4l2-h264.o

INSTALLDIR		:=$(TARGETDIR)/system/bin

EXTRA_LDFLAGS	+=-lpthread
EXTRA_LDFLAGS	+=-lrt

#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common
