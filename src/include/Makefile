#
#------------------------------------------------------------------------------

FULL_VERSION := $(shell git describe --long --tags --dirty | sed s/-/./g | sed s/^v// )
MAJOR := $(shell echo '$(FULL_VERSION)' | awk -F. {'print $$1'})
MINOR := $(shell echo '$(FULL_VERSION)' | awk -F. {'print $$2'})
REV := $(shell echo '$(FULL_VERSION)' | awk -F. {'print $$3'})

FILE_VERSION := "version.h"


all: version

version:
	@echo "Generated version.h"
	@echo "\n\
	#ifndef __VERSION_H__\n\
	#define __VERSION_H__\n\
	#define VERSION_MAJOR		$(MAJOR)\n\
	#define VERSION_MINOR		$(MINOR)\n\
	#define VERSION_REVISION	$(REV)\n\
	#define VERSION_STRING		\"$(MAJOR).$(MINOR).$(REV)\"\n\
	#endif /* __VERSION_H__ */\n\
	" > $(FILE_VERSION)

clean:
	@rm -rf $(FILE_VERSION)
