
SHELL					:=/bin/bash
DEBUG					?=1
MODEL					?=PiCAM
VERSION					:=0.1
CORES					:= $(shell cat /proc/cpuinfo | grep process | wc -l)

#------------------------------------------------------------------------------

include $(BASEDIR)/build/Rules.$(MODEL)
include $(BASEDIR)/build/Rules.head
