#!/bin/bash

DPKG_DIR=$PIC_ROOT_DIR/dpkg
VERSION_FILE=$PIC_SRC_DIR/include/version.h
DPKG_CONTROL_FILE=$DPKG_DIR/DEBIAN/control

Version=`cat $VERSION_FILE | grep STRING | awk -F\" '{ print $2 }'`
Package="picam"


generateControl() {
	cat >$DPKG_CONTROL_FILE <<EOF
Package: $Package
Version: $Version
Priority: optional
Architecture: all
Section: Other
Maintainer: HyunSuk-Lee <peanutstars.lee@gmail.com>
Description: Raspberry Pi with Cameras
 .
EOF

}

generateControl
pushd $PIC_ROOT_DIR
dpkg --build dpkg
mv dpkg.deb $Package-$Version.deb
popd
