#
#------------------------------------------------------------------------------

ifndef  BASEDIR
BASEDIR			:=$(shell pwd)/../..
endif
include $(BASEDIR)/Rules.mk

#------------------------------------------------------------------------------

CXXTARGET		:= rtspsvr
OBJS			:= rtspsvr.o

INSTALLDIR		:=$(TBINDIR)
LIVEINCDIR		:=$(BASEDIR)/external/install/usr/local/include
LIVELIBDIR		:=$(BASEDIR)/external/install/usr/local/lib

#EXTRA_CPPFLAGS	+=-std=c++11
EXTRA_CPPFLAGS  +=-D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64
EXTRA_CPPFLAGS	+=-I$(LIVEINCDIR)/UsageEnvironment
EXTRA_CPPFLAGS	+=-I$(LIVEINCDIR)/groupsock
EXTRA_CPPFLAGS	+=-I$(LIVEINCDIR)/liveMedia
EXTRA_CPPFLAGS	+=-I$(LIVEINCDIR)/BasicUsageEnvironment
EXTRA_CPPFLAGS	+=-DSOCKLEN_T=socklen_t -DBSD=1

EXTRA_LDFLAGS	+=$(LIVELIBDIR)/libliveMedia.a $(LIVELIBDIR)/libgroupsock.a $(LIVELIBDIR)/libBasicUsageEnvironment.a $(LIVELIBDIR)/libUsageEnvironment.a
EXTRA_LDFLAGS	+=-lpthread
EXTRA_LDFLAGS	+=-lrt

#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.common
