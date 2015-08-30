import subprocess
from subprocess import CalledProcessError
from vboxapi import VirtualBoxManager
from pyadb import ADB

VBOX_MGR = VirtualBoxManager()
ADB_PORT = '5555'
CONSTANTS = VBOX_MGR.constants

def clone_vm(parent_name, clone_name):
    cmd = 'VBoxManage clonevm --name ' + clone_name
    cmd += ' --register ' + parent_name
    return subprocess.call(cmd, shell = True)

def delete_vm(name):
    cmd = 'VBoxManage unregistervm --delete ' + name
    return subprocess.call(cmd, shell = True)
    
class vbox_controller:
    def __init__(self, name):
        vbox = VBOX_MGR.vbox
        self.session = VBOX_MGR.getSessionObject(vbox)
        self.vm = vbox.findMachine(name)
        self.name = name
        self.adb = ADB('adb')
        self.ip = ''
        self.cmd_ip = ''
        self.network_key = None
        
    def start(self):
        self.vm.launchVMProcess(self.session, "gui", '').waitForCompletion(5000)
        
    def lock_session(self):
        self.vm.lockMachine(self.session, CONSTANTS.LockType_Shared)

    def unlock_session(self):
        self.session.unlockMachine()

    def get_cmd_ip(self):
        mac = self.session.machine.getNetworkAdapter(1).MACAddress.lower()
        mac_formatted = ''
        for i in range(6):
            position = i * 2
            mac_formatted += mac[position:position + 2]
            if i != 5:
                mac_formatted += ':'
        try:
            output = subprocess.check_output('arp -a | grep ' + mac_formatted, shell=True)
            self.cmd_ip = self.parse_arp(output)
            return self.cmd_ip
        except CalledProcessError as e:
            print('Could not run arp command')
            self.cmd_ip = ''
            return ''
    
    def parse_arp(self, arp_output):
        start = arp_output.find('(')
        if start == -1:
            return None
        end = arp_output.find(')', start + 1)
        if end == -1:
            return None
        return arp_output[start + 1:end]

    def stop(self):
        self.session.console.powerDown()
    
    def attach_to_bridge(self, bridge):
        subprocess.call('VBoxManage controlvm ' + self.name + ' nic1 bridged ' +  bridge, shell = True)

    def attach_to_switch(self, switch):
        print 'Attaching ', self.name, ' to ', switch
        if switch is not None:
            subprocess.call('VBoxManage controlvm ' + self.name + ' nic1 generic VDE', shell = True)
            subprocess.call('VBoxManage controlvm ' + self.name + ' nicproperty1 network=/tmp/' + switch, shell = True)
        else:
            subprocess.call('VBoxManage controlvm ' + self.name + ' nic1 null', shell = True)

    def move_to_lan(self, ip, netmask, network_key, gateway = None):
        self.run_cmd('ifconfig eth0 ' + ip + ' netmask ' + netmask + ' up')
        if not gateway is None:
            self.run_cmd('route add default gw ' + gateway + ' dev eth0 ')
        self.ip = ip
        self.network_key = network_key
        
    def connect_adb(self):
        self.get_cmd_ip()
        if self.cmd_ip in subprocess.check_output("adb devices", shell = True):
            subprocess.call('adb disconnect ' + self.cmd_ip + ':' + ADB_PORT, shell = True)
        # i've got a bug in adb and can't specify the port, so it must be the 5555 default one
        subprocess.call('adb connect ' + self.cmd_ip, shell=True)
        subprocess.call('adb -s ' + self.cmd_ip + ':' + ADB_PORT + ' root', shell=True)
        subprocess.call('adb connect ' + self.cmd_ip, shell=True)


    def run_cmd(self, cmd):
        return subprocess.check_output("adb -s " + self.cmd_ip + ':' + ADB_PORT + " shell " + cmd, shell=True)

    def push_file(self, file, location):
        return subprocess.call("adb -s " + self.cmd_ip + ':' + ADB_PORT + ' push ' + file + ' ' + location, shell = True)
