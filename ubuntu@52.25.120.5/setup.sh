#!/bin/bash

OUT=../install

sudo apt-get install gcc g++ bcc iasl xsltproc uuid-dev zlib1g-dev libidl-dev \
                libsdl1.2-dev libxcursor-dev libasound2-dev libstdc++5 \
                libpulse-dev libxml2-dev libxslt1-dev \
                python-dev libqt4-dev qt4-dev-tools libcap-dev \
                libxmu-dev mesa-common-dev libglu1-mesa-dev \
                linux-kernel-headers libcurl4-openssl-dev libpam0g-dev \
                libxrandr-dev libxinerama-dev libqt4-opengl-dev makeself \
                libdevmapper-dev default-jdk python-central

#wget http://download.virtualbox.org/virtualbox/4.3.26/VirtualBox-4.3.26.tar.bz2

#tar jxf VirtualBox-4.3.26.tar.bz2

if [ -z "$OUTPUT"]; then
	OUTPUT=$OUT
	mkdir install
fi

cd VirtualBox-4.3.26

#./configure --disable-hardening --enable-vde --out-path=$OUTPUT

. $OUTPUT/env.sh
kmk

cd $OUTPUT/linux.x86/release/bin/src
make
