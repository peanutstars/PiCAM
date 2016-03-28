
SHELL					:=/bin/bash
DEBUG					?=1
MODEL					?=PiCAM
VERSION					:=0.1
CORES					:= $(shell cat /proc/cpuinfo | grep process | wc -l)
BUILDDIR				:= $(BASEDIR)/../build

#------------------------------------------------------------------------------

include $(BUILDDIR)/Rules.$(MODEL)
include $(BUILDDIR)/Rules.head
