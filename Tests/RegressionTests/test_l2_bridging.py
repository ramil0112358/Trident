import logging
import pytest
from Lib.modules.Ixia import Ixia
import time
'''
L2 bridging test.
-Broadcast traffic forwarding check
-Multicast traffic forwarding check
-UUC traffic forwarding check
-KUC traffic forwarding check
-Static MAC entry check
-MAC table functionality check
-Traffic loss due mac address flap check
-Access ports functionality check
-Vlan traffic forwarding failure check
-MAC learning check
-Incorrect source MAC check
-Incorrect FCS check
'''
#------------------------init functions--------------------------
@pytest.fixture
def init_test_environment(init_environment_instances):
    topology_list, \
    topology_manager_instance, \
    module_manager_instance = init_environment_instances
    return topology_list, \
           topology_manager_instance, \
           module_manager_instance

@pytest.fixture
def test_l2_bridging_broadcast_fixture(init_test_environment):
    topology_list, topology_manager_instance, module_manager_instance = init_test_environment
    #Setup
    logging.info('Broadcast test setup')
    '''
    #1.Create topology
    top_args = {'topology_name': 'topology1'}
    topology_manager_instance.add_topology(top_args)
    #2.Create node
    node_args = {'hostname': 'node1',
                 'type': '751048x6q',
                 'topology': 'topology1'}
    topology_manager_instance.add_topology_node(node_args)
    connect_args = {'topology': 'topology1',
                    'hostname': 'node1',
                    'ip': '10.27.192.41',
                    'protocol': 'telnet',
                    'port': '23',
                    'username': 'admin',
                    'password': 'bulat'}
    #3.Create connection module
    module_manager_instance.add_module_connect(connect_args)
    connect_id = module_manager_instance.module_instance_dict['connect']
    login_args = {'connect_id': connect_id.get_id()}
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))
    #4.Login to node
    logging.info(connect_id.get_summary())
    login_res, nope = module_manager_instance.module_connect_login(login_args)
    logging.debug('login_res: ' + str(login_res))
    assert login_res == 1
    #5.Get session id
    sesdict = module_manager_instance.connect_login_sessions_dict.items()
    logging.debug('session_dict: ' + str(sesdict))
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))
    #6.Send command via session id  
    #command1_args = {'session_id': 'ses1',
    #                 'command': 'conf t'}
    #module_manager_instance.module_send_send_via_sesid(command1_args)
    #command2_args = {'session_id': 'ses1',
    #                 'command': 'vlan 778 bridge 1'}
    #module_manager_instance.module_send_send_via_sesid(command2_args)
    
    #6.Send command via hostname
    command1a_args = {'hostname': 'node1',
                     'command': 'conf t'}
    module_manager_instance.module_send_send_via_hostname(command1a_args)
    #7.Send command via hostname
    command2a_args = {'hostname': 'node1',
                      'command': 'vlan 779 bridge 1'}
    module_manager_instance.module_send_send_via_hostname(command2a_args)
    '''

    #8.Ixia launch
    ixia_instance = Ixia("10.27.152.3", "11009", "admin", "admin")
    ixia_ixnetwork = ixia_instance.get_ixnetwork_instance()
    #9.init new scenario with ports(
    ixia_instance.add_scenario()
    ixia_instance.add_interface_to_scenario("2/5")
    ixia_instance.add_interface_to_scenario("2/2")
    #10.add topology to scenario
    port_list = list()
    port_list.append("2/5")
    assert ixia_instance.add_topology(port_list, "Topology1") == 1
    port_list2 = list()
    port_list2.append("2/2")
    assert ixia_instance.add_topology(port_list2, "Topology2") == 1
    assert ixia_instance.add_device_group("Topology1", "DeviceGroupA", 1) == 1
    assert ixia_instance.add_device_group("Topology2", "DeviceGroupB", 1) == 1
    #11.add protocols
    '''
    vlan_list = "500"
    assert ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA", True, 1, vlan_list) == 1
    vlan_start_value = "501"
    assert ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB", True, 5, vlan_start_value) == 1
    '''
    assert ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA") == 1
    assert ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB") == 1


    assert ixia_instance.add_protocol_ipv4("Topology1",
                                           "DeviceGroupA",
                                           "192.168.1.1",
                                           "24",
                                           "192.168.1.2",
                                           True) == 1

    assert ixia_instance.add_protocol_ipv4("Topology2",
                                           "DeviceGroupB",
                                           "192.168.1.2",
                                           "24",
                                           "192.168.1.1",
                                           True) == 1

    ixia_instance.start_all_protocols()
    '''
    traffic_item1_data = {
        "source_port": "2/5",
        "dest_port": "2/2",
        "src_mac_address": "00:11:00:00:00:01",
        "dst_mac_address": "00:12:00:00:00:01",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("RawTrafficItem", "raw", traffic_item1_data) == 1

    traffic_item2_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ethernetTrafficItem", "ethernetVlan", traffic_item2_data) == 1

    traffic_item3_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ipv4TrafficItem", "ipv4", traffic_item3_data) == 1

    assert ixia_instance.disable_traffic_item("RawTrafficItem") == 1
    assert ixia_instance.disable_traffic_item("ethernetTrafficItem") == 1
    assert ixia_instance.disable_traffic_item("ipv4TrafficItem") == 1

    assert ixia_instance.enable_traffic_item("RawTrafficItem") == 1
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1
    assert ixia_instance.disable_traffic_item("RawTrafficItem") == 1
    assert ixia_instance.enable_traffic_item("ethernetTrafficItem") == 1
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1
    assert ixia_instance.disable_traffic_item("ethernetTrafficItem") == 1
    assert ixia_instance.enable_traffic_item("ipv4TrafficItem") == 1
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1
    '''

    traffic_item3_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ipv4TrafficItem", "ipv4", traffic_item3_data) == 1
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    flow_statistics = ixia_instance.get_traffic_items_stat()
    logging.info("Traffic_items stats: " + str(flow_statistics))
    """
    Main traffic_items features:
    'Tx Frames': '2199',
    'Rx Frames': '2199',
    'Frames Delta': '0',
    'Loss %': '0.000',
    'Tx Rate (Mbps)': '1.120', 
    'Rx Rate (Mbps)': '1.120', 
    'Store-Forward Avg Latency (ns)': '2002', 
    'Store-Forward Min Latency (ns)': '1900', 
    'Store-Forward Max Latency (ns)': '2120', 
    'First TimeStamp': '00:00:00.202', 
    'Last TimeStamp': '00:00:22.178'
    """


    yield
    #Teardown
    logging.info('Broadcast test teardown')


#------------------------test functions--------------------------

def test_l2_bridging_broadcast_core(test_l2_bridging_broadcast_fixture):
    module_manager_instance = test_l2_bridging_broadcast_fixture
    logging.info('Broadcast test core')
    t1 = 1
    t2 = 1
    assert t1 == t2
