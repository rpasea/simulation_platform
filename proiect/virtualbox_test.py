#!/usr/bin/python

import subprocess
import threading
import time

from simulation_platform import network
from simulation_platform import  virtualbox_controller

from simulation_platform.network import network
from simulation_platform.virtualbox_controller import vbox_controller


vbox1 = vbox_controller("Android1")
vbox2 = vbox_controller("Android2")

vbox1.lock_session()
vbox2.lock_session()
#vbox1.start()

#net1.start()


#time.sleep(60)
#vbox1.get_cmd_ip()

vbox1.connect_adb()
#time.sleep(1)
print(vbox1.run_cmd('netcfg'))
vbox2.connect_adb()
#time.sleep(1)
print(vbox2.run_cmd('netcfg'))

#net1.attach_container(vbox1)
#time.sleep(1)

#print(vbox1.run_cmd('netcfg'))

net1 = network('10.1.1.0', '255.255.255.0')
net1.start()

net2 = network('10.1.2.0', '255.255.255.0')
net2.start()

time.sleep(3)
net1.attach_container(vbox1)
print(vbox1.run_cmd('arp'))

net1.attach_container(vbox2)
print(vbox1.run_cmd('arp'))

net1.detach_container(vbox1)
net2.attach_container(vbox2)
#net1.detach_container(vbox2)

net1.stop()
net2.stop()

vbox1.unlock_session()
vbox2.unlock_session()

#vbox1.stop()

