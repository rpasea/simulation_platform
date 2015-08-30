#!/usr/bin/python

import sys, getopt
import simulation_platform.networking.communicator
import simulation_platform.event_queue.simulation_event_queue

from simulation_platform.command_file import json_classes
from simulation_platform.simulation import start_simulation
from simulation_platform import event_queue


help_message = 'Usage:\n\
./start.py --port <port> --root_address <address> --root_port <port> --command_file <file>\n\
Where:\n\
port - port on which local communicator is opened. If not specified, a default port will be\n\
used \n\
command_file - parameter which specifies location of file containing commands. If not specified,\n\
an attempt to connect to root address must be made\n\
commands\n\
root_address - address of root node. If a command file is given, this address must be the local\n\
address on which the other nodes must connect\n\
root_port - port of root node. If not specified, the default port will be used\n'

def parse_command_file(path):
    with open(path, 'r') as command_file:
        content = command_file.read()
    return json_classes.from_json(content)

def print_callback(event):
    print type(event).__name__

def main(argv):
    port = simulation_platform.networking.communicator.PORT
    root_addr = None
    root_port = simulation_platform.networking.communicator.PORT
    command_file = None
    try:
        opts, args = getopt.getopt(argv, "h", ["port=", "root_address=", "root_port=", "command_file=", "help"])
    except getopt.GetoptError:
        print help_message
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print help_message
            sys.exit()
        elif opt in ("--port"):
            port = int(arg)
        elif opt in ("--root_address"):
            root_addr = arg
        elif opt in ("--root_port"):
            root_port = int(arg)
        elif opt in ("--command_file"):
            command_file = arg
    if root_addr is None and command_file is None:
        print "Can't run without a root addresses or a command file."
        print help_message
        sys.exit()
    
    commands = None    
    if command_file is not None:
        commands = parse_command_file(command_file)
    start_simulation(port, root_addr, root_port, commands)
        
        
if __name__ == "__main__":
    main(sys.argv[1:])
    '''
    file = json_classes.CommandFile()
    host = json_classes.Host('127.0.0.1')
    file.hosts.append(host)
    file.vms.append(json_classes.AndroidVM('1'))
    file.vms.append(json_classes.AndroidVM('2'))
    file.simulation = json_classes.Simulation(30)
    file.simulation.events.append(json_classes.ChangeNetworkEvent('2', '10.1.1.0', '255.255.255.0', 10))
    file.simulation.events.append(json_classes.ChangeNetworkEvent('1', '10.1.1.0', '255.255.255.0', 12))
    print json_classes.to_json(file)
    '''
