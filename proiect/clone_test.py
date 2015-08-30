#!/usr/bin/python

from simulation_platform.virtualbox_controller import clone_vm
from simulation_platform.virtualbox_controller import delete_vm

if __name__ == "__main__":
    print clone_vm('Android1', 'Clone1')
    print delete_vm('Clone1')
