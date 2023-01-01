from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from Lib.SystemConstants import ixia_server_ip
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
import time
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
        self.traffic_items = list()

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

    def add_device_group(self,
                         device_group_topology_name,
                         device_group_name,
                         multiplier)->bool:

        topology_check = False
        for topology in self.topology_list:
            if topology.Name == device_group_topology_name:
                topology_check = True

        if topology_check == False:
            logging.info("Topology " + device_group_topology_name + " not found")
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
                    logging.debug("New device_group id instance: " + str(id(new_device_group)))
                    logging.debug("New device_group name is: " + str(new_device_group.Name))
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

    def get_device_group_instance_by_name(self,
                                          device_group_topology_name,
                                          device_group_name):
        device_group_instance = None
        logging.debug("current device_group_dict: " + str(self.device_group_dict))
        device_group_list = self.device_group_dict[device_group_topology_name]
        logging.debug("current device_group_list: " + str(device_group_list))
        for device_group in device_group_list:
            logging.debug("device_group: " + str(device_group))
            logging.debug("device_group.Name: " + str(device_group.Name))
            if device_group.Name == device_group_name:
                device_group_instance = device_group

        return device_group_instance

    def update_device_group(self,
                            device_group_topology_name,
                            device_group_name):
        self.get_device_group_instance_by_name(device_group_topology_name,
                                               device_group_name).update()

    def add_protocol_ethernet(self,
                    device_group_topology_name,
                    device_group_name,
                    enablevlan=False,
                    vlancount=0, #vlan multitag (vlancount > 1) doesnt support yet
                    vlanid_first=None)->bool:

        device_group_instance = self.get_device_group_instance_by_name(device_group_topology_name,device_group_name)
        if device_group_instance == None:
            return 0
        else:
            ethernet_instance = device_group_instance.Ethernet.add(UseVlans=enablevlan, VlanCount=vlancount)
            #logging.info("ethernet_instance: " + str(ethernet_instance))
            #topologies_count = len(self.topology_list)
            topology_instance = self.get_topology_by_name(device_group_topology_name)
            topology_index = self.topology_list.index(topology_instance)
            new_topology_mac = '00:1' + str(topology_index + 1) + ':00:00:00:01'
            if device_group_instance.Multiplier == 1:
                ethernet_instance.Mac.Single(new_topology_mac)
                if vlanid_first != None:
                    vlan_instance = ethernet_instance.Vlan.find()
                    #logging.info("vlan_instance before: " + str(vlan_instance))
                    vlan_instance.VlanId.Single(vlanid_first)
                    #logging.info("vlan_instance after: " + str(vlan_instance))
            else:
                ethernet_instance.Mac.Increment(new_topology_mac, '00:00:00:00:00:01')
                if vlanid_first != None:
                    vlan_instance = ethernet_instance.Vlan.find()
                    vlan_instance.VlanId.Increment(vlanid_first, '1')
            #self.ethernet_list.append(ethernet_instance)
            logging.info("Ethernet " + str(ethernet_instance.Name) + " successfully created")
            return 1

    def remove_protocol_ethernet(self,
                                device_group_topology_name,
                                device_group_name,
                                ethernet_name) -> bool:

        device_group_instance = self.get_device_group_instance_by_name(device_group_topology_name, device_group_name)
        if device_group_instance == None:
            return 0
        else:
            target_ethernet = device_group_instance.Ethernet.find(Name=ethernet_name)
            target_ethernet.remove()
            logging.info("Ethernet " + str(ethernet_name) + " successfully removed")
            return 1

    def add_protocol_ipv4(self,
                    device_group_topology_name,
                    device_group_name,
                    ip_address,
                    ip_prefix,
                    ip_gateway,
                    resolve_gateway) -> bool:

        device_group_instance = None
        device_group_list = self.device_group_dict[device_group_topology_name]
        for device_group in device_group_list:
            #logging.info("device_group_name: " + str(device_group.Name))
            if device_group.Name == device_group_name:
                device_group_instance = device_group
        #logging.info("device_group_instance: " + str(device_group_instance))
        if device_group_instance == None:
            return 0
        else:
            ethernet_instance = device_group_instance.Ethernet.find()
            ipv4_instance = ethernet_instance.Ipv4.add()
            #logging.info("Multiplier: " + str(device_group_instance.Multiplier))
            if device_group_instance.Multiplier == 1:
                ip_address_list = list()
                ip_prefix_list = list()
                ip_gateway_list = list()
                resolve_gateway_list = list()
                #logging.info("Multiplier == 1")
                ip_address_list.append(ip_address)
                ipv4_instance.Address.ValueList(ip_address_list)
                ip_prefix_list.append(ip_prefix)
                ipv4_instance.Prefix.ValueList(ip_prefix_list)
                ip_gateway_list.append(ip_gateway)
                ipv4_instance.GatewayIp.ValueList(ip_gateway_list)
                resolve_gateway_list.append(resolve_gateway)
                ipv4_instance.ResolveGateway.ValueList(resolve_gateway_list)
            else:
                #logging.info("Multiplier != 1")
                ipv4_instance.Address.Increment(ip_address,"0.0.0.1")
                ipv4_instance.GatewayIp.Single(ip_gateway)
                ipv4_instance.Prefix.Single(ip_prefix)
                ipv4_instance.ResolveGateway.Single(resolve_gateway)
            logging.info("IPv4 " + str(ipv4_instance.Name) + " successfully added")
            #logging.info("IPv4: " + str(ipv4_instance))
            return 1

        return 0

    def remove_protocol_ipv4(self,
                             device_group_topology_name,
                             device_group_name,
                             ipv4_name) -> bool:

        device_group_instance = self.get_device_group_instance_by_name(device_group_topology_name, device_group_name)
        if device_group_instance == None:
            return 0
        else:
            target_ipv4 = device_group_instance.Ethernet.find().IPv4.find(Name=ipv4_name)
            target_ipv4.remove()
            logging.info("IPv4 " + str(ipv4_name) + " successfully removed")
            return 1

    def get_ipv4_resolve_gateway_info(self,
                                      device_group_topology_name,
                                      device_group_name,
                                      ipv4_name) -> bool:
        device_group_instance = self.get_device_group_instance_by_name(device_group_topology_name, device_group_name)
        if device_group_instance == None:
            return 0
        else:
            target_ipv4 = device_group_instance.Ethernet.find().IPv4.find(Name=ipv4_name)
            logging.info('Target ipv4: ' + str(target_ipv4))
            #resolve_gateway = target_ipv4.Ipv4.find().ResolveGateway
            #logging.info('Resolve gateway info: ' + str(resolve_gateway.info))

    def add_traffic_item(self, ti_name, ti_type, ti_data) -> bool:

        """
        ti_name: (str) traffic item name
        ti_type: (str) "raw"/"ethernetVlan"/"ipv4"
        ti_data: (dict)
        ti_data for type raw:
            {"source_port":"1/1",
             "dest_port":"1/2",
             "src_mac_address":"0011.0000.0001",
             "dst_mac_address":"0012.0000.0001",
             "framerate_type":"framePerSecond",
             "framerate_value":"100",
             "frame_size":"1400",
             "bidir":0,
             "control_type:"continuous"}
        ti_data for type ethernet:
            {"source_device_group_name":"DeviceGroupA",
             "dest_device_group_name":"DeviceGroupB",
             "framerate_type":"framePerSecond",
             "framerate_value":"100",
             "frame_size":"1400",
             "bidir":0,
             "control_type:"continuous"}
        ti_data for type ipv4:
            {"source_device_group_name":"DeviceGroupA",
             "dest_device_group_name":"DeviceGroupB",
             "framerate_type":"framePerSecond",
             "framerate_value":"100",
             "frame_size":"1400",
             "bidir":0,
             "control_type:"continuous"}
        """
        if ti_type == "raw":
            self.traffic_items.append(
                self.ixia_ixnetwork.Traffic.TrafficItem.add(
                    Name=ti_name,
                    BiDirectional=ti_data['bidir'],
                    TrafficType=ti_type,
                    AllowSelfDestined=False,
                    RouteMesh='oneToOne'))

            # works only for raw traffic type
            SourcePort = self.ixia_ixnetwork.Vport.find(Name=ti_data['source_port']).Protocols.find()
            DestPort = self.ixia_ixnetwork.Vport.find(Name=ti_data['dest_port']).Protocols.find()
            self.traffic_items[-1].EndpointSet.add(Sources=SourcePort, Destinations=DestPort)

            # update the frame rate,frame size,transmission control
            traffic_config = self.traffic_items[-1].ConfigElement.find()
            #logging.info('traffic_config before: ' + str(traffic_config.FrameRate))
            #traffic_config = self.traffic_items.ConfigElement.find()
            traffic_config.FrameRate.update(Rate=ti_data['framerate_value'], Type=ti_data['framerate_type'])
            traffic_config.TransmissionControl.update(Type=ti_data['control_type'])
            traffic_config.FrameSize.update(FixedSize=ti_data['frame_size'])
            #logging.info('traffic_config after: ' + str(traffic_config.FrameRate))

            # adjust Ethernet source ans destination fields
            # still doesnt work, TrackingEnabled works but src and dst fields doesnt work
            source_mac = traffic_config.Stack.find(
                StackTypeId='ethernet').Field.find(
                FieldTypeId='ethernet.header.sourceAddress')
            src_mac_address_list = list()
            src_mac_address_list.append(ti_data['src_mac_address'])
            source_mac.update(
                ValueType='singleValue',
                ValueList=src_mac_address_list,
                TrackingEnabled=True)

            destination_mac = traffic_config.Stack.find(
                StackTypeId='ethernet').Field.find(
                FieldTypeId='ethernet.header.destinationAddress')
            dst_mac_address_list = list()
            dst_mac_address_list.append(ti_data['dst_mac_address'])
            destination_mac.update(
                ValueType='singleValue',
                ValueList=dst_mac_address_list,
                TrackingEnabled=True)

            return True

        if ti_type == "ethernetVlan":
            self.traffic_items.append(
                self.ixia_ixnetwork.Traffic.TrafficItem.add(
                    Name=ti_name,
                    BiDirectional=ti_data['bidir'],
                    TrafficType=ti_type,
                    AllowSelfDestined=False,
                    RouteMesh='oneToOne'))

            #logging.info("traffic_item: " + str(self.ixia_ixnetwork.Traffic.TrafficItem))
            source_device_group = None
            dest_device_group = None

            for device_group_list in self.device_group_dict.values():
                for device_group in device_group_list:
                    if device_group.Name == ti_data['source_device_group_name']:
                        source_device_group = device_group
                    if device_group.Name == ti_data['dest_device_group_name']:
                        dest_device_group = device_group

            if source_device_group == None:
                logging.debug("source_device_group: " + str(source_device_group) + " not found")
                return False
            if dest_device_group == None:
                logging.debug("dest_device_group: " + str(dest_device_group) + " not found")
                return False

            source_ethernet = source_device_group.Ethernet.find()
            destination_ethernet = dest_device_group.Ethernet.find()

            self.traffic_items[-1].EndpointSet.add(
                Sources=source_ethernet,
                Destinations=destination_ethernet)

            # update the frame rate,frame size,transmission control
            traffic_config = self.traffic_items[-1].ConfigElement.find()
            traffic_config.FrameRate.update(Type=ti_data['framerate_type'], Rate=ti_data['framerate_value'])
            traffic_config.TransmissionControl.update(Type=ti_data['control_type'])
            traffic_config.FrameSize.update(FixedSize=ti_data['frame_size'])

            return True

        if ti_type == "ipv4":
            self.traffic_items.append(
                self.ixia_ixnetwork.Traffic.TrafficItem.add(
                    Name=ti_name,
                    BiDirectional=ti_data['bidir'],
                    TrafficType=ti_type,
                    AllowSelfDestined=False,
                    RouteMesh='oneToOne'))

            source_device_group = None
            dest_device_group = None

            for device_group_list in self.device_group_dict.values():
                for device_group in device_group_list:
                    if device_group.Name == ti_data['source_device_group_name']:
                        source_device_group = device_group
                    if device_group.Name == ti_data['dest_device_group_name']:
                        dest_device_group = device_group

            if source_device_group == None:
                logging.debug("source_device_group: " + str(source_device_group) + " not found")
                return False
            if dest_device_group == None:
                logging.debug("dest_device_group: " + str(dest_device_group) + " not found")
                return False

            source_ipv4 = source_device_group.Ethernet.find().Ipv4.find()
            destination_ipv4 = dest_device_group.Ethernet.find().Ipv4.find()

            self.traffic_items[-1].EndpointSet.add(
                Sources=source_ipv4,
                Destinations=destination_ipv4)

            # update the frame rate,frame size,transmission control
            traffic_config = self.traffic_items[-1].ConfigElement.find()
            traffic_config.FrameRate.update(Type=ti_data['framerate_type'], Rate=ti_data['framerate_value'])
            traffic_config.TransmissionControl.update(Type=ti_data['control_type'])
            traffic_config.FrameSize.update(FixedSize=ti_data['frame_size'])

            return True
        return False

    def apply_and_start_traffic_items(self) -> bool:
        for traffic_item in self.traffic_items:
            traffic_item.EndpointSet.find().refresh()
            traffic_item.Tracking.find().TrackBy = ['trackingenabled0']
            traffic_item.Generate()
        self.ixia_ixnetwork.Traffic.Apply()
        time.sleep(1)
        self.ixia_ixnetwork.Traffic.Start()
        time.sleep(1)
        return True

    def stop_traffic_items(self) -> bool:
        self.ixia_ixnetwork.Traffic.Stop()
        return True

    def enable_traffic_item(self, ti_name) -> bool:
        traffic_item = None
        traffic_item = self.ixia_ixnetwork.Traffic.find().TrafficItem.find(Name=ti_name)
        if traffic_item == None:
            logging.info("traffic item: " + str(ti_name) + " not found")
            return False
        traffic_item.update(Enabled=True)
        return True

    def disable_traffic_item(self, ti_name) -> bool:
        traffic_item = None
        traffic_item = self.ixia_ixnetwork.Traffic.find().TrafficItem.find(Name=ti_name)
        if traffic_item == None:
            logging.info("traffic item: " + str(ti_name) + " not found")
            return False
        traffic_item.update(Enabled=False)
        return True

    def get_traffic_items_stat(self) -> bool:
        flow_statistics = StatViewAssistant(self.ixia_ixnetwork, 'Flow Statistics')
        flow_statistics = vars(flow_statistics.Rows)
        final_statistics = dict()
        traffic_item_statistics = dict()
        traffic_item_name = str
        for row_data in flow_statistics['_row_data']:
            column_index = 0
            for column_data in flow_statistics['_column_headers']:
                traffic_item_statistics.update({column_data: row_data[column_index]})
                if column_index == 2:
                    traffic_item_name = row_data[column_index]
                column_index = column_index + 1
            traffic_item_statistics_copy = dict(traffic_item_statistics)
            final_statistics[traffic_item_name] = traffic_item_statistics_copy
            traffic_item_statistics.clear()
        return final_statistics

    def remove_traffic_item(self, ti_name) -> bool:
        traffic_item = None
        traffic_item = self.ixia_ixnetwork.Traffic.find().TrafficItem.find(Name=ti_name)
        if traffic_item == None:
            logging.info("traffic item: " + str(ti_name) + " not found")
            return False
        traffic_item.remove()
        return True

    def start_all_protocols(self) -> bool:
        self.ixia_ixnetwork.StartAllProtocols()

    def stop_all_protocols(self) -> bool:
        self.ixia_ixnetwork.StopAllProtocols()







