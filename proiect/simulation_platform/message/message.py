import pickle
import struct

int_size = struct.calcsize('>I')

types = {
    0 : 'NetworkQueryMessage',
    'NetworkQueryMessage' : 0,
    1 : 'NetworkReplyMessage',
    'NetworkReplyMessage' : 1,
    2 : 'RoutingMessage',
    'RoutingMessage' : 2,
    3 : 'IdRequest',
    'IdRequest' : 3,
    4 : 'IdReply',
    'IdReply' : 4,
    5 : 'IdentifyRequest',
    'IdentifyRequest' : 5,
    6 : 'IdentifyReply',
    'IdentifyReply' : 6,
    7 : 'NetworkMessage',
    'NetworkMessage' : 7,
    8 : 'IpRequest',
    'IpRequest' : 8,
    9 : 'IpRelease',
    'IpRelease' : 9,
    10 : 'IpResponse',
    'IpResponse' : 10,
    11 : 'SimulationMessage',
    'SimulationMessage' : 11,
    12 : 'PlatformStartedMessage',
    'PlatformStartedMessage' : 12,
    13 : 'PlatformStopMessage',
    'PlatformStopMessage' : 13,
    14 : 'StartNodes',
    'StartNodes' : 14,
    15 : 'VmStarted',
    'VmStarted' : 15,
    16 : 'ChangeNetworkMessage',
    'ChangeNetworkMessage' : 16,
}

class SerializedMessage:
    def __init__(self, message, serialize = True):
        if serialize:
            self.string = pickle.dumps(message, -1)
        else:
            self.string = message
        self.size = len(self.string)

    def __str__(self):
        return struct.pack('>I', self.size) + self.string

    def get_message(self):
        return pickle.loads(self.string)

class NetworkQueryMessage:
    def __init__(self, address, netmask):
        self.type = types['NetworkQueryMessage']
        self.address = address
        self.netmask = netmask

class NetworkReplyMessage:
    def __init__(self, address, netmask, switch):
        self.type = types['NetworkReplyMessage']
        self.address = address
        self.netmask = netmask
        self.switch = switch

class RoutingMessage:
    def __init__(self, source_id, dest_id, msg):
        self.type = types['RoutingMessage']
        self.source = source_id
        self.dest_id = dest_id
        self.message = msg
    
class IdRequest:
    def __init__(self):
        self.type = types['IdRequest']

class IdReply:
    def __init__(self, id):
        self.type = types['IdReply']
        self.id = id
        
class IdentifyRequest:
    def __init__(self, id):
        self.type = types['IdentifyRequest']
        self.id = id
        
class IdentifyReply:
    def __init__(self, id, address):
        self.type = types['IdentifyReply']
        self.id = id
        self.address = address
        
class NetworkMessage:
    def __init__(self, key, msg):
        self.type = types['NetworkMessage']
        self.key = key
        self.msg = msg

class IpRequest:
    def __init__(self):
        self.type = types['IpRequest']

class IpRelease:
    def __init__(self, ip):
        self.type = types['IpRelease']
        self.ip = ip

class IpResponse:
    def __init__(self, ip):
        self.type = types['IpResponse']
        self.ip = ip
        
class SimulationMessage:
    def __init__(self, msg):
        self.type = types['SimulationMessage']
        self.msg = msg

class PlatformStartedMessage:
    def __init__(self):
        self.type = types['PlatformStartedMessage']
        
class PlatformStopMessage:
    def __init__(self):
        self.type = types['PlatformStopMessage']
        
class StartVmsMessage:
    def __init__(self, vms):
        self.type = types['StartNodes']
        self.vms = vms
        
class VmStartedMessage:
    def __init__(self, vm, status):
        self.type = types['VmStarted']
        self.vm = vm
        self.status = status
        
class ChangeNetworkMessage:
    def __init__(self, vm, address, netmask):
        self.type = types['ChangeNetworkMessage']
        self.vm = vm
        self.address = address
        self.netmask = netmask