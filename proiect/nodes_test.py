#!/usr/bin/python

from simulation_platform.centralized_topology import CentralizedTopology
from simulation_platform.simulator_node import simulator_node
from simulation_platform import  virtualbox_controller


import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Need to specify container name and port"
        sys.exit(1)
    container_name = sys.argv[1]
    port = int(sys.argv[2])
    remote_host = None
    remote_port = port
    if len(sys.argv) > 3:
        remote_host = sys.argv[3]
    if len(sys.argv) > 4:
        remote_port = int(sys.argv[4])
    
    top1 = CentralizedTopology(port)
    #top2 = CentralizedTopology(7601)
    simulator_node1 = simulator_node(top1)
    #simulator_node2 = simulator_node(top2)
    if remote_host is None:
        top1.start(simulator_node1)
    else:
        top1.start(simulator_node1, (remote_host, remote_port))
    #top2.start(simulator_node2, ('localhost', 7600))
    container = virtualbox_controller.vbox_controller(container_name)
    container.lock_session()
    container.connect_adb()

    simulator_node1.create_network('10.1.1.0', '255.255.255.0', str(port))
    simulator_node1.start_container(container_name)
    #print top2.address_of_id(top2.get_local_id())
    
    raw_input("Press Enter to end...")
    
    simulator_node1.move_container_to_network(container_name, '10.1.1.0', '255.255.255.0')
    raw_input("Press Enter to end...")
    #top2.communicator.stop()
    top1.stop()