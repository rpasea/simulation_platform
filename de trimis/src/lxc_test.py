#!/usr/bin/python

import subprocess
import threading
import time
import lxc
from lxc_controller import lxc_controller
from network import network


net1 = network("192.168.101.0", "255.255.255.248")
net2 = network("192.168.102.0", "255.255.255.248")

net1.start()
net2.start()

c1 = lxc_controller("ubuntu1")
c2 = lxc_controller("ubuntu2")

c1.start()
c2.start()

time.sleep(5)

net1.attach_container(c1)
net2.attach_container(c2)

print('\n')

c1.container.attach_wait(lxc.attach_run_command,
                                   ['arp-scan', '--interface=eth0', '--localnet'])
net1.detach_container(c1)
net2.attach_container(c1)

print('\n')
c1.container.attach_wait(lxc.attach_run_command,
                                   ['arp-scan', '--interface=eth0', '--localnet'])
c1.stop()
c2.stop()
