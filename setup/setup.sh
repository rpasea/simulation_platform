#!/bin/bash

START_DIR=$(pwd)
OUT=/opt/VirtualBox

########## INSTALL PREREQUISITES ################

sudo apt-get install gcc g++ bcc iasl xsltproc uuid-dev zlib1g-dev libidl-dev \
                libsdl1.2-dev libxcursor-dev libasound2-dev libstdc++5 \
                libpulse-dev libxml2-dev libxslt1-dev python-pip vde2\
                python-dev libqt4-dev qt4-dev-tools libcap-dev \
                libxmu-dev mesa-common-dev libglu1-mesa-dev android-tools-adb\
                linux-kernel-headers libcurl4-openssl-dev libpam0g-dev \
                libxrandr-dev libxinerama-dev libqt4-opengl-dev makeself \
                libdevmapper-dev default-jdk mkisofs libvpx-dev build-essential \
		openjdk-6-jdk texlive-latex-base \
                texlive-latex-extra texlive-latex-recommended \
                texlive-fonts-extra texlive-fonts-recommended

if [ $(uname -m) == 'x86_64' ]; then
	sudo apt-get install libc6-dev-i386 lib32gcc1 gcc-multilib \
                lib32stdc++6 g++-multilib
fi

########## DOWNLOAD VBOX SOURCES ############

wget http://download.virtualbox.org/virtualbox/4.3.26/VirtualBox-4.3.26.tar.bz2

tar jxf VirtualBox-4.3.26.tar.bz2

####### COMPILE AND INSTALL VBOX #######################

if [ -z "$OUTPUT"]; then
	OUTPUT=$OUT
	mkdir $OUTPUT
fi

cd VirtualBox-4.3.26

./configure --disable-hardening --enable-vde --out-path=$OUTPUT

. $OUTPUT/env.sh
kmk

cd $(find $OUTPUT -maxdepth 1 -name linux.*)/release/bin/src
make
sudo make install

sudo modprobe vboxdrv
sudo chmod a+rw /dev/vboxdrv

cd -
cd $(find $OUTPUT -maxdepth 1 -name linux.*)/release/bin/sdk/installer
sudo env VBOX_INSTALL_PATH=../../ python vboxapisetup.py install

######## INSTALL NEEDED PYTHON PACKAGES ##########

cd $START_DIR
wget https://pypi.python.org/packages/source/p/py2-ipaddress/py2-ipaddress-3.4.1.tar.gz
tar -xzf py2-ipaddress-3.4.1.tar.gz
cd py2-ipaddress-3.4.1
sudo python setup.py install
cd -
rm py2-ipaddress-3.4.1.tar.gz
sudo rm -rf py2-ipaddress-3.4.1
sudo pip install jsonpickle

######## CREATE HYCCUPS USER AND SET KEYS #########

sudo useradd -m -p $(perl -e 'print crypt("hyccups", "hyccups");') -s /bin/bash hyccups
sudo cp -r ssh/ /home/hyccups/.ssh
sudo find /home/hyccups/.ssh -exec chown hyccups:hyccups {} +
sudo echo PATH=$(find $OUTPUT -maxdepth 3 -name bin):$PATH >> /home/hyccups/.bashrc i
file=$(find $OUTPUT -maxdepth 3 -name bin)
sudo env file=$file sh -c 'echo PATH=$PATH:$file >> /home/hyccups/.bashrc'
##################### COPY AND REGISTER THE BASE VM ###########
sudo mkdir -p /home/hyccups/.config/VirtualBox
sudo cp -r $START_DIR/base_vm/Android1 /home/hyccups/.config/VirtualBox
sudo find /home/hyccups/.config -exec chown hyccups:hyccups {} +
sudo adduser hyccups vboxusers
sudo xhost local:hyccups
VBOXMANAGE=$file/VBoxManage
sudo su hyccups -c "$VBOXMANAGE registervm Android1/Android1.vbox"  
