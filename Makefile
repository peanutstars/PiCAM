#

ifndef PIC_ROOT_DIR
$(error "YOU MUST DO 'export PIC_ROOT_DIR=/absolute/path/to/root/dir/'.")
endif

SRCDIR		:= $(PIC_ROOT_DIR)/src
SCRIPTSDIR  := $(PIC_ROOT_DIR)/scripts

ifndef	BASEDIR
BASEDIR			:=$(SRCDIR)
endif
include $(BASEDIR)/Rules.mk


.PHONY: dpkg

all:
	$(MAKE) -C $(SRCDIR)

clean:
	$(MAKE) -C $(SRCDIR) clean

install:
	@rm -rf $(TARGETDIR)
	$(MAKE) -C $(SRCDIR) install

dpkg:
	@$(SCRIPTSDIR)/mkdpkg.sh


