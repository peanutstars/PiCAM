#!/bin/bash

DPKG_DIR=$PIC_ROOT_DIR/dpkg
VERSION_FILE=$PIC_SRC_DIR/include/version.h
DPKG_CONTROL_FILE=$DPKG_DIR/DEBIAN/control

Version=`cat $VERSION_FILE | grep STRING | awk -F\" '{ print $2 }'`
Package="picam"
Architecture="unknown"


checkArchitecture() {
	Arch=`uname -m`
	case "$Arch" in
		x86_64)
			Architecture="amd64"
			;;
		armv7l)
			Architecture="armhf"
			;;
		*)
			Architecture="unknown"
			;;
	esac
	[ "$Architecture" == "unknown" ] && echo -e "\n\tArchitecture is unknown.\n" && exit 1
}

generateControl() {
	cat >$DPKG_CONTROL_FILE <<EOF
Package: $Package
Version: $Version
Depends: miniupnpc
Priority: optional
Architecture: $Architecture
Section: Video
Maintainer: peanutstars <peanutstars.lee@gmail.com>
Description: Streaming Video with Web-Cameras(C920)
 It is streaming video with web-cameras, currently supported only C920.
EOF

}

checkArchitecture
generateControl
pushd $PIC_ROOT_DIR
fakeroot dpkg --build dpkg
mv dpkg.deb $Package-$Version.deb
popd
