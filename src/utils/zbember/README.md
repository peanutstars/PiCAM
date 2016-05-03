## Ember USB Dongle for Zigbee

### HW Spec

- Chip Set : EM3585
- Bootloader Image : EmberZNet5.4.2-GA/tool/bootloader-em3585/app-bootloader/app-bootloader.s37
- Application Image : EmberZNet5.4.2-GA/em35xx-ezsp-images/EM3585/ncp-uart-xon-xoff-use-with-serial-uart-btl-5.4.2.s37


### SW Compile

It works for compiling zbember, if the EmberZNet5.4.2-GA folder is placed at /work/project/zigbee/EmberZNet5.4.2-GA.
If you are different building environments, please add Ember.mk file and the contents are as follows.

```Makefile
EMBER_BASE		= /Your/Absolute/Path/For/EmberZNet5.4.2-GA
EMBER_APP_BASE	= $(EMBER_BASE)/app/builder/zbember
```

