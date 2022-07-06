from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from Lib.SystemConstants import ixia_server_ip

import logging
'''
Class represents methods 
to work with ixia traffic generator.
'''
class Ixia():

    def __init__(self,
                 resthost,
                 restport,
                 username,
                 password
                 ):
        self.resthost = resthost
        self.restport = restport
        self.username = username
        self.password = password
        self.ixia_testplatform_instance = self.connect_to_testplatform()
        logging.info(str(self.ixia_testplatform_instance))
        self.ixia_sessions = self.ixia_testplatform_instance.Sessions.add()
        self.ixia_ixnetwork = self.ixia_sessions.Ixnetwork
        self.ixia_globals = self.ixia_ixnetwork.Globals
        self.ixia_topology_instance = self.ixia_globals.Topology
        self.ixia_phyports = list()
        self.ixia_vports = list()
        self.topology_list = list()
        self.device_group_dict = dict()
        self.ethernet_list = list()

    def get_ixnetwork_instance(self):
        return self.ixia_ixnetwork

    def connect_to_testplatform(self):
        message = 'Connection to the Ixnetwork REST API on host {}'.format(
            self.resthost + ':' + self.restport)
        logging.info(message)
        try:
            self.testplatform_instance = TestPlatform(self.resthost, self.restport)
            self.testplatform_instance.Authenticate(self.username, self.password)
            logging.info('Successfully connected to ixia chassis')
            return self.testplatform_instance
        except Exception as error:
            logging.info(error)
            return None

    def add_scenario(self):
        self.ixia_ixnetwork.NewConfig()
        self.ixia_chassis = self.ixia_ixnetwork.AvailableHardware.Chassis.add(Hostname=ixia_server_ip)

    def add_interface_to_scenario(self, interface):
        ixia_vport = self.ixia_ixnetwork.Vport.add(Name=interface)
        ixia_vport_list = list()
        ixia_vport_list.append(ixia_vport)
        self.ixia_vports.append(ixia_vport)
        logging.info('ADD_IXIA_VPORT: ' + str(ixia_vport.Name))
        slot, port = interface.split('/')
        ports_dict = {"Arg1":ixia_server_ip,
                      "Arg2":slot,
                      "Arg3":port,}
        ixia_phyport = dict(ports_dict)
        ixia_phyport_list = list()
        ixia_phyport_list.append(ixia_phyport)
        self.ixia_phyports.append(ixia_phyport)
        logging.info('ADD_IXIA_PHYPORT: ' + str(ixia_phyport))
        self.ixia_chassis.Card.find(CardId=slot)
        self.ixia_ixnetwork.AssignPorts(ixia_phyport_list, list(), ixia_vport_list, True)

    def add_interfaces_to_scenario(self, portlist):
        pass

    def add_topology(self, portlist, topology_name="Noname")->bool:
        '''
        Addition new topology to scenario.
        By default one DeviceGroup with one host ethernet protocol will be created.

        Args:
            portlist: ports for new topology
            topology_name: new topology name
        '''
        #logging.info("all ports:" + str(self.ixia_ixnetwork.GetAllPorts))
        vport_list = list()

        for port in portlist:
            for vport in self.ixia_vports:
                if vport.Name == port:
                    vport_list.append(vport)

        for topology in self.topology_list:
            if topology.Name == topology_name:
                logging.info("Cant create topology.Topology " + str(topology.Name) + " already exist")
                return 0

        new_topology = self.ixia_ixnetwork.Topology.add(Name=topology_name, Ports=vport_list)
        self.topology_list.append(new_topology)
        self.device_group_dict[topology_name] = list()
        #logging.info(self.topology_list)
        return 1

    def get_topology_by_name(self, topology_name):
        for topology in self.topology_list:
            if topology.Name == topology_name:
                return topology
        return 0

    def add_device_group(self, device_group_name, device_group_topology_name, multiplier)->bool:

        topology_check = False
        for topology in self.topology_list:
            if topology.Name == device_group_topology_name:
                topology_check = True

        if topology_check == False:
            logging.info("Topology " + device_group_topology_name + "not found")
            return 0

        current_device_groups = self.device_group_dict
        #logging.info("List len check: " + str(len(self.device_group_dict)))
        if len(self.device_group_dict) > 0:
            for topology_name, device_groups_list in current_device_groups.items():
                if topology_name == device_group_topology_name:
                    for device_group in device_groups_list:
                        if device_group.Name == device_group_name:
                            logging.info("Can't create device group.Device group " +
                                str(device_group.Name) + " already exist")
                            return 0

                    topology = self.get_topology_by_name(topology_name)
                    new_device_group = topology.DeviceGroup.add(Multiplier=multiplier, Name=device_group_name)
                    self.device_group_dict[topology_name].append(new_device_group)
                    #logging.info("Check for not empty dg_list: " + str(self.device_group_dict))
                    return 1
            logging.info("Can't create device group.Topology " + device_group_topology_name + " not found")
            return 0
        else:
            device_groups_list = list()
            topology = self.get_topology_by_name(device_group_topology_name)
            new_device_group = topology.DeviceGroup.add(Multiplier=multiplier, Name=device_group_name)
            device_groups_list.append(new_device_group)
            self.device_group_dict[device_group_topology_name] = device_groups_list
            #logging.info("Check for empty dg_list: " + str(self.device_group_dict))
            return 1
        return 0

    def add_protocol_ethernet(self,
                     device_group_name,
                     device_group_topology_name,
                     enablevlan,
                     vlancount,
                     vlanid = None,
                     multiplier = 1)->bool:

        device_group_list = self.device_group_dict[device_group_topology_name]
        for device_group in device_group_list:
            if device_group.Name == device_group_name:
                device_group_instance = device_group

        ethernet_instance = device_group_instance.Ethernet.add(UseVlans=enablevlan, VlanCount=vlancount)
        ethernet_instance.Vlan.find()
        topologies_count = len(self.topology_list)
        new_topology_mac = '00:1' + str(topologies_count) + ':00:00:00:01'
        if multiplier == 1:
            ethernet_instance.Mac.Single(new_topology_mac)
            if vlanid != None:
                ethernet_instance.Vlan.Single(vlanid)
        else:
            ethernet_instance.Mac.Increment(new_topology_mac, '00:00:00:00:00:01')
            if vlanid != None:
                ethernet_instance.Vlan.Increment(vlanid, '1')
        self.ethernet_list.append(ethernet_instance)
        return True



        '''
        # Add device_group
        # instance.device_group_1 = instance.topology[-1].DeviceGroup.add(
        #    Multiplier=Multiplier)
        instance.device_groups.append(
            instance.topology[-1].DeviceGroup.add(
                Multiplier=Multiplier))

        # Configuring Ethernet
        # instance.ethernets = instance.device_groups[-1].Ethernet.add(
        #    UseVlans=None,
        #    VlanCount=None)
        instance.ethernets.append(instance.device_groups[-1].Ethernet.add(
            UseVlans=None,
            VlanCount=None))
        # instance.vlans = instance.ethernets[-1].Vlan.find()
        instance.vlans.append(instance.ethernets[-1].Vlan.find())
        instance.ethernets[-1].Mac.Single('00:00:00:00:00:01')
        '''


    '''
    def add_protocol(instance, ProtocolData):
        
        #Args:
        #    instance: (Session): A global process instance
        #    ProtocolData  (dict): ProtocolData
        #     amount_of_hosts = Topology.DeviceGroup.Multiplier

        if len(instance.topology) == 0:
            raise Exception('Topology not found')

        if 'topology_name' in ProtocolData:
            # check out current topology index by name
            loop_index = 0
            current_topology_index = 0
            for current_topology in instance.topology:
                if current_topology.DescriptiveName == ProtocolData['topology_name']:
                    current_topology_index = loop_index
                    break
                loop_index = loop_index + 1

            logging.warning('Adding {protocol} protocol to {TopologyName} topology'.format(
                protocol=ProtocolData['protocol'],
                TopologyName=instance.topology[current_topology_index].DescriptiveName))

            # Ethernet
            if ProtocolData['protocol'] == "ethernet":

                # set vlan
                if 'vlan' in ProtocolData:
                    if ProtocolData['vlan'] == 'untag':
                        instance.ethernets[current_topology_index].update(
                            UseVlans=False,
                            VlanCount=1)
                    else:
                        instance.ethernets[current_topology_index].update(
                            UseVlans=True,
                            VlanCount=1)
                        instance.vlans[current_topology_index].VlanId.Single(ProtocolData['vlan'])
                        # instance.ethernets[topology_index].Vlan.find()

                # set_mac_address
                if 'mac-address' in ProtocolData:
                    instance.ethernets[current_topology_index].Mac.Single(ProtocolData['mac-address'])

            # ipv4
            if ProtocolData['protocol'] == "ipv4":

                instance.ipv4.append(instance.ethernets[current_topology_index].Ipv4.add())
                ipv4_instance = instance.ipv4[current_topology_index].find()
                ip_address_list = list()
                ip_gateway_list = list()
                ip_prefix_list = list()

                # set ipv4 values
                if 'ip-address' in ProtocolData:
                    ip_address_list.append(ProtocolData['ip-address'])
                    ipv4_instance.Address.ValueList(ip_address_list)

                if 'ip-gateway' in ProtocolData:
                    ip_gateway_list.append(ProtocolData['ip-gateway'])
                    ipv4_instance.GatewayIp.ValueList(ip_gateway_list)

                if 'ip_prefix' in ProtocolData:
                    ip_prefix_list.append(ProtocolData['ip_prefix'])
                    ipv4_instance.Prefix.ValueList(ip_prefix_list)
    '''



