# This Makefile defines how to build a unix host application connected to an
# Ember NCP EZSP uart device.  This also works for Windows machines running
# Cygwin.

# Variables

# If using a different compiler than GCC, you can create a makefile
# that overrides the following variables.  
#   COMPILER - Compiler binary path
#   LINKER - Linker binary path
#   ARCHIVE - Optional archive tool, only necessary for building a library.
#     Must also set GENERATE_LIBRARY := 1 in your makefile.
#   COMPILER_INCLUDES - Any additional compiler includes each prefixed with -I
#   COMPILER_DEFINES - Any additional compiler defines each prefixed with -D
#   COMPILER_FLAGS - The set of compiler flags (not including dependencies)
#   LINKER_FLAGS - The set of linker flags
#   ARCHIVE_FLAGS - The set of archive tool flags.
#   DEPENDENCY_FLAGS - The set of dependency generation flags used to generate
#     dependencies at the same time compilation is executed.
#   DEPENDENCY_POST_PROCESS - An optional post processing step for massaging
#     generated depenendencies.  Only necessary when using a compiler on the 
#     non-native platform (e.g. Windows compiler on Linux)
#   PLATFORM_HEADER_FILE - The header file defining the basic int8u, int32u,
#     and other typedefs and platform elements.
#   BOARD_HEADER_FILE - The header file describing any board specific options.
#   ARCHIVE_EXTENSION - The file extension for archives if not using the standard
#     .a file extension.
#
# Then pass the makefile to this one on the command line with:
#   "make -C app/builder/zbember/Makefile INCLUDE_MAKEFILE=my-custom.mak"
#   or 
#   "cd app/builder/zbember; make"
#

ifdef EMBER_APP_BASE
VPATH			= $(EMBER_APP_BASE)
else
EMBER_APP_BASE	=.
endif

ifdef INCLUDE_MAKEFILE
  include $(INCLUDE_MAKEFILE)
endif  

COMPILER ?= gcc
LINKER   ?= gcc
ARCHIVE  ?= ar

ARCHIVE_EXTENSION ?= .a

CC = $(COMPILER)
LD = $(LINKER)
SHELL = /bin/sh

ifneq ($(CURDIR),$(shell dirname $(abspath $(lastword $(MAKEFILE_LIST)))))
$(error This makefile should only be invoked under its current directory ($(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))))
endif

COMPILER_INCLUDES ?= 

INCLUDES= \
  $(COMPILER_INCLUDES) \
  -I$(EMBER_APP_BASE)/../../.. \
  -I$(EMBER_APP_BASE)/../../../app/builder/zbember \
  -I$(EMBER_APP_BASE)/../../../app/ezsp-uart-host \
  -I$(EMBER_APP_BASE)/../../../app/framework/cli \
  -I$(EMBER_APP_BASE)/../../../app/framework/include \
 \
  -I$(EMBER_APP_BASE)/../../../app/framework/security \
  -I$(EMBER_APP_BASE)/../../../app/framework/util \
  -I$(EMBER_APP_BASE)/../../../app/util \
  -I$(EMBER_APP_BASE)/../../../app/util/common \
  -I$(EMBER_APP_BASE)/../../../app/util/ezsp \
  -I$(EMBER_APP_BASE)/../../../app/util/serial \
  -I$(EMBER_APP_BASE)/../../../app/util/zigbee-framework \
  -I$(EMBER_APP_BASE)/../../../hal/.. \
  -I$(EMBER_APP_BASE)/../../../hal \
  -I$(EMBER_APP_BASE)/../../../hal/micro/generic \
  -I$(EMBER_APP_BASE)/../../../hal/micro/unix/host \
  -I$(EMBER_APP_BASE)/../../../stack

APP_BUILDER_OUTPUT_DIRECTORY=.
APP_BUILDER_CONFIG_HEADER=$(APP_BUILDER_OUTPUT_DIRECTORY)/zbember.h
APP_BUILDER_STORAGE_FILE=$(APP_BUILDER_OUTPUT_DIRECTORY)/zbember_endpoint_config.h

PLATFORM_HEADER_FILE ?= \"../../../hal/micro/unix/compiler/gcc.h\"
BOARD_HEADER_FILE    ?= \"../../../hal/micro/unix/host/board/host.h\"

DEFINES = \
  $(COMPILER_DEFINES) \
  -DPHY_EM250 \
  -DAF_UART_HOST \
  -DUNIX \
  -DUNIX_HOST \
  -DPHY_NULL \
  -DBOARD_HOST \
  -DCONFIGURATION_HEADER=\"../../../app/framework/util/config.h\" \
  -DEZSP_HOST \
  -DGATEWAY_APP \
  -DZA_GENERATED_HEADER=\"$(APP_BUILDER_CONFIG_HEADER)\" \
  -DATTRIBUTE_STORAGE_CONFIGURATION=\"$(APP_BUILDER_STORAGE_FILE)\" \
  -DPLATFORM_HEADER=$(PLATFORM_HEADER_FILE) \
  -DBOARD_HEADER=$(BOARD_HEADER_FILE) \
  


COMPILER_FLAGS ?= \
  -Wall \
  -ggdb \
  -O0

APPLICATION_FILES= \
  ../../../app/builder/zbember/call-command-handler.c \
  ../../../app/builder/zbember/callback-stub.c \
  ../../../app/builder/zbember/stack-handler-stub.c \
  ../../../app/builder/zbember/cli.c \
  ../../../app/builder/zbember/zbember_callbacks.c \
  ../../../app/framework/cli/core-cli.c \
  ../../../app/framework/cli/network-cli.c \
  ../../../app/framework/cli/option-cli.c \
  ../../../app/framework/cli/plugin-cli.c \
  ../../../app/framework/cli/security-cli.c \
  ../../../app/framework/cli/zcl-cli.c \
  ../../../app/framework/cli/zdo-cli.c \
  ../../../app/framework/security/af-node.c \
  ../../../app/framework/security/af-security-common.c \
  ../../../app/framework/security/af-trust-center.c \
  ../../../app/framework/security/crypto-state.c \
  ../../../app/framework/util/af-event.c \
  ../../../app/framework/util/af-main-common.c \
  ../../../app/framework/util/af-main-host.c \
  ../../../app/framework/util/attribute-size.c \
  ../../../app/framework/util/attribute-storage.c \
  ../../../app/framework/util/attribute-table.c \
  ../../../app/framework/util/client-api.c \
  ../../../app/framework/util/message.c \
  ../../../app/framework/util/multi-network.c \
  ../../../app/framework/util/print.c \
  ../../../app/framework/util/print-formatter.c \
  ../../../app/framework/util/process-cluster-message.c \
  ../../../app/framework/util/process-global-message.c \
  ../../../app/framework/util/service-discovery-common.c \
  ../../../app/framework/util/service-discovery-host.c \
  ../../../app/framework/util/time-util.c \
  ../../../app/framework/util/util.c \
  ../../../app/util/common/library.c \
  ../../../app/util/serial/command-interpreter2.c \
  ../../../app/util/zigbee-framework/zigbee-device-common.c \
  ../../../app/util/zigbee-framework/zigbee-device-host.c \
  ../../../stack/framework/event-control.c \
  ../../../hal/micro/generic/buzzer-stub.c \
  ../../../hal/micro/generic/crc.c \
  ../../../hal/micro/generic/led-stub.c \
  ../../../hal/micro/generic/mem-util.c \
  ../../../hal/micro/generic/random.c \
  ../../../hal/micro/generic/system-timer.c \
  ../../../hal/micro/unix/host/micro.c \
  ../../../app/framework/plugin/address-table/address-table-management.c \
  ../../../app/framework/plugin/address-table/address-table-cli.c \
  ../../../app/framework/plugin/address-table/address-table-host.c \
  ../../../app/framework/plugin/concentrator/concentrator-support.c \
  ../../../app/framework/plugin/concentrator/concentrator-support-cli.c \
  ../../../app/util/source-route-common.c \
  ../../../app/util/source-route-host.c \
  ../../../app/framework/plugin/counters/counters-cli.c \
  ../../../app/framework/plugin/counters/counters-ota-host.c \
  ../../../app/framework/plugin/counters/counters-host.c \
  ../../../app/framework/plugin/ezmode-commissioning/ez-mode.c \
  ../../../app/framework/plugin/ezmode-commissioning/ez-mode-cli.c \
  ../../../app/framework/plugin/find-and-bind/find-and-bind-initiator.c \
  ../../../app/framework/plugin/find-and-bind/find-and-bind-target.c \
  ../../../app/framework/plugin/form-and-join/form-and-join-afv2.c \
  ../../../app/util/common/form-and-join.c \
  ../../../app/util/common/form-and-join-host-adapter.c \
  ../../../app/framework/plugin/fragmentation/fragmentation.c \
  ../../../app/framework/plugin/fragmentation/fragmentation-cli.c \
  ../../../app/framework/plugin/fragmentation/fragmentation-host.c \
  ../../../app/framework/plugin/identify/identify.c \
  ../../../app/framework/plugin/identify/identify-cli.c \
  ../../../app/framework/plugin/identify-feedback/identify-feedback.c \
  ../../../app/framework/plugin/interpan/interpan.c \
  ../../../app/framework/plugin/interpan/interpan-host.c \
  ../../../app/framework/plugin/network-find/network-find.c \
  ../../../app/framework/plugin/ota-common/ota-common.c \
  ../../../app/framework/plugin/ota-server/ota-server.c \
  ../../../app/framework/plugin/ota-server/ota-server-page-request.c \
  ../../../app/framework/plugin/ota-server/ota-server-cli.c \
  ../../../app/framework/plugin/ota-server-policy/ota-server-policy.c \
  ../../../app/framework/plugin/ota-storage-common/ota-storage-common.c \
  ../../../app/framework/plugin/ota-storage-common/ota-storage-common-cli.c \
  ../../../app/framework/plugin/ota-storage-posix-filesystem/ota-storage-linux.c \
  ../../../app/framework/plugin/permit-join-manager/permit-join-manager.c \
  ../../../app/framework/plugin/poll-control-client/poll-control-client.c \
  ../../../app/framework/plugin/poll-control-client/poll-control-client-cli.c \
  ../../../app/framework/plugin/price-common/price-common.c \
  ../../../app/framework/plugin/price-common/price-common-time.c \
  ../../../app/framework/plugin/price-common/price-common-cli.c \
  ../../../app/framework/plugin/reporting/reporting.c \
  ../../../app/framework/plugin/reporting/reporting-cli.c \
  ../../../app/framework/plugin/simple-main/simple-main.c \
  ../../../app/framework/plugin/sleepy-message-queue/sleepy-message-queue.c \
  ../../../app/framework/plugin/sleepy-message-queue/sleepy-message-queue-cli.c \
  ../../../app/framework/plugin/stack-diagnostics/stack-diagnostics.c \
  ../../../app/framework/plugin/time-server/time-server.c \
  ../../../app/util/ezsp/ezsp-callbacks.c \
  ../../../app/util/ezsp/ezsp-enum-decode.c \
  ../../../app/util/ezsp/ezsp-frame-utilities.c \
  ../../../app/util/ezsp/ezsp.c \
  ../../../app/util/ezsp/serial-interface-uart.c \
  ../../../app/ezsp-uart-host/ash-host-io.c \
  ../../../app/ezsp-uart-host/ash-host-queues.c \
  ../../../app/ezsp-uart-host/ash-host-ui.c \
  ../../../app/ezsp-uart-host/ash-host.c \
  ../../../hal/micro/generic/ash-common.c \
  ../../../app/framework/plugin-host/file-descriptor-dispatch/file-descriptor-dispatch.c \
  ../../../app/framework/plugin-host/gateway/gateway-support.c \
  ../../../app/framework/plugin-host/gateway/backchannel-support.c \
  ../../../app/framework/plugin-host/gateway/gateway-support-cli.c \
  ../../../app/framework/plugin-host/ncp-configuration/ncp-configuration.c \
  ../../../app/util/serial/ember-printf-convert.c \
  ../../../app/util/serial/linux-serial.c \


OUTPUT_DIR=$(APP_BUILDER_OUTPUT_DIRECTORY)/build
OUTPUT_DIR_CREATED= $(OUTPUT_DIR)/created
EXE_DIR=$(OUTPUT_DIR)/exe
# Build a list of object files from the source file list, but all objects
# live in the $(OUTPUT_DIR) above.  The list of object files
# created assumes that the file part of the filepath is unique
# (i.e. the bar.c of foo/bar.c is unique across all sub-directories included).
APPLICATION_OBJECTS= $(shell echo $(APPLICATION_FILES) | xargs -n1 echo | sed -e 's^.*/\(.*\)\.c^$(OUTPUT_DIR)/\1\.o^')

ifdef GENERATE_LIBRARY
TARGET_FILE= $(EXE_DIR)/zbember$(ARCHIVE_EXTENSION)
else
TARGET_FILE= $(EXE_DIR)/zbember
endif

# -MMD and -MF generates Makefile dependencies while at the same time compiling.
# -MP notes to add a dummy 'build' rule for each header file.  This 
# prevent a problem where a removed header file will generate an error because a
# dependency references it but it can't be found anymore.
DEPENDENCY_FLAGS ?= -MMD -MP -MF $(@D)/$*.d 

# Dependency post process is a way to massage generated dependencies.
# This is necessary for example when using Make under Cygwin but compiling
# using a native Windows compiler that generates native Windows paths
# that Cygwin will choke on.  Or if compiling on Linux using Wine to run a 
# Windows compiler, a similar problem can occur.  
DEPENDENCY_POST_PROCESS ?=

CPPFLAGS= $(INCLUDES) $(DEFINES) $(COMPILER_FLAGS) $(DEPENDENCY_FLAGS)
LINKER_FLAGS ?=

ifdef NO_READLINE
  CPPFLAGS += -DNO_READLINE
else
  LINKER_FLAGS +=  \
    -lreadline \
    -lncurses 
endif

ARCHIVE_FLAGS ?= rus

# Rules

all: $(TARGET_FILE)

ifneq ($(MAKECMDGOALS),clean)
-include $(APPLICATION_OBJECTS:.o=.d)
endif

ifdef GENERATE_LIBRARY
$(TARGET_FILE): $(APPLICATION_OBJECTS)
	$(ARCHIVE) $(ARCHIVE_FLAGS) $(TARGET_FILE) $^
	@echo -e '\n$@ build success'
else
$(TARGET_FILE): $(APPLICATION_OBJECTS)
	$(LD) $^ $(LINKER_FLAGS) -o $(TARGET_FILE)
	@echo -e '\n$@ build success'
endif

clean:
	rm -rf $(OUTPUT_DIR)

$(OUTPUT_DIR_CREATED):
	mkdir -p $(OUTPUT_DIR)
	mkdir -p $(EXE_DIR)
	touch $(OUTPUT_DIR_CREATED)

# To facilitate generating all output files in a single output directory, we
# must create separate .o and .d rules for all the different sub-directories
# used by the source files.
# If additional directories are added that are not already in the
# $(APPLICATION_FILES) above, new rules will have to be created below.

# Object File rules

$(OUTPUT_DIR)/%.o: ../../../app/builder/zbember/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/ezsp-uart-host/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/framework/cli/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/address-table/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/aes-cmac/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/basic/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/button-joining/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/calendar-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/calendar-common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/calendar-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/color-control/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/comms-hub-function/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/concentrator/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/counters/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/device-database/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/device-management-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/device-management-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/device-query-service/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/diagnostic-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/door-lock-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/drlc/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/drlc-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/eeprom/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ember-minimal-printf/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/end-device-support/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/esi-management/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/events-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/events-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ezmode-commissioning/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/find-and-bind/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/form-and-join/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/fragmentation/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/gas-proxy-function/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/gbcs-device-log/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/gbcs-gas-meter/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/gbz-message-controller/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/general-response-commands/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/groups-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/groups-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/hc-11073-tunnel/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ias-zone-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ias-zone-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/identify/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/identify-feedback/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/interpan/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/key-establishment/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/level-control/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/messaging-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/messaging-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/meter-mirror/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/meter-snapshot-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/meter-snapshot-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/meter-snapshot-storage/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/mn-price-passthrough/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/network-creator/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/network-find/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/network-steering/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/on-off/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-bootload/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-client-policy/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-server-policy/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-storage-common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-storage-posix-filesystem/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-storage-simple/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-storage-simple-eeprom/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/ota-storage-simple-ram/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/partner-link-key-exchange/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/permit-join-manager/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/poll-control-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/poll-control-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/prepayment-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/prepayment-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/prepayment-snapshot-storage/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/price-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/price-common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/price-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/reporting/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-gdp/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-gdp-identification-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-gdp-identification-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-mso/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-mso-ir-rf-database-originator/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-mso-ir-rf-database-recipient/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-profile/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc11/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc20/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc20-action-mapping-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc20-action-mapping-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc20-ha-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/rf4ce-zrc20-ha-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/scenes/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/scenes-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/simple-clock/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/simple-main/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/simple-metering-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/simple-metering-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/sleepy-message-queue/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/smart-energy-registration/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/stack-diagnostics/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/standalone-bootloader-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/standalone-bootloader-common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/standalone-bootloader-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/standard-printf-support/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/test-harness/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/time-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/trust-center-backup/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/trust-center-keepalive/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/trust-center-nwk-key-update-broadcast/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/trust-center-nwk-key-update-periodic/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/trust-center-nwk-key-update-unicast/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/tunneling-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/tunneling-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/xmodem-sender/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-commissioning/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-identify-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-level-control-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-on-off-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-scenes-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-scenes-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-utility-client/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin/zll-utility-server/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/aes-software/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/ezsp/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/file-descriptor-dispatch/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/gateway/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/ncp-configuration/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../framework/plugin-host/unix-printf/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)



$(OUTPUT_DIR)/%.o: ../../../app/framework/security/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/framework/util/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/common/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/ezsp/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/gateway/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/serial/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../app/util/zigbee-framework/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../stack/framework/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../hal/micro/generic/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)

$(OUTPUT_DIR)/%.o: ../../../hal/micro/unix/host/%.c $(OUTPUT_DIR_CREATED)
	$(CC) $(CPPFLAGS) -c $< -o $(OUTPUT_DIR)/$(@F)
	$(DEPENDENCY_POST_PROCESS)


# Dependency rules
# No explicit rules.  Dependencies are generated as part of the compile step.
