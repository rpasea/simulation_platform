#!/bin/sh
ifconfig eth0 192.168.101.2 netmask 255.255.255.248 up
route add default gw 192.168.101.1 dev eth0
