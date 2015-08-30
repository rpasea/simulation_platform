from simulation_platform.centralized_topology import CentralizedTopology
from simulation_platform.simulator_node import simulator_node

if __name__ == "__main__":
	top1 = CentralizedTopology(7600)
	top2 = CentralizedTopology(7601)
	
	simulator_node1 = simulator_node(top1)
	simulator_node2 = simulator_node(top2)
	
	top1.start(simulator_node1)
	top2.start(simulator_node2, ('localhost', 7600))

	print top2.address_of_id(top2.get_local_id())
	
	top2.communicator.stop()
	top1.communicator.stop()