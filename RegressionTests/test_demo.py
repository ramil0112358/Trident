import logging
import pytest


# ------------------------init functions--------------------------
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
    # Setup
    logging.info('Broadcast test setup')

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
                    'ip': '10.27.193.2',
                    'protocol': 'console',
                    'port': '2037',
                    'username': 'admin',
                    'password': 'bulat'}
                    
    #3.Create connection module
    module_manager_instance.add_module_connect(connect_args)
    connect_id = module_manager_instance.module_instance_dict['connect']
    login_args = {'connect_id': connect_id.get_id()}
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))
    
    #4.Login to node
    logging.info(connect_id.get_summary())
    login_res = module_manager_instance.module_connect_login(login_args)
    logging.debug('login_res: ' + str(login_res))
    assert login_res == 1

    #4a.Init node
    hostname = "TR202"
    mgmt_info = {"ip": "10.27.192.38", "mask": "24", "gateway": "10.27.192.254"}

    software_image_path = \
        "10.121.0.147/RZN_SWITCHES/distrib/releases-v22.160/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.2-GA2.0-full"

    '''
    software_image_path = \
        "10.121.0.147/RZN_SWITCHES/distrib/releases-v22.165/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.3-GA2.0-full"
    '''
    '''
    software_image_path = \
        "10.121.0.147/RZN_SWITCHES/distrib/releases-v22.237/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.4-GA2.0-full"
    '''
    topology_manager_instance.init_topology_node('node1',
                                                 module_manager_instance,
                                                 hostname,
                                                 mgmt_info,
                                                 software_image_path)

    """
    #5.Get session id
    sesdict = module_manager_instance.connect_login_sessions_dict.items()
    logging.debug('session_dict: ' + str(sesdict))
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))

    #6.Send command via session id
    command1_args = {'session_id': 'ses1:node1:telnet:10.27.192.38:23',
                     'command': 'conf t'}
    module_manager_instance.module_send_send_via_sesid(command1_args)
    command2_args = {'session_id': 'ses1:node1:telnet:10.27.192.38:23',
                     'command': 'vlan 778 bridge 1'}
    module_manager_instance.module_send_send_via_sesid(command2_args)

    #7 Logout
    logout_args = {'connect_id': connect_id.get_id(), 'session_id': 'ses1:node1:telnet:10.27.192.38:23'}
    logout_res, nope = module_manager_instance.module_connect_logout(logout_args)
    logging.info('logout_res: ' + str(logout_res))
    """
    pass
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

    #11.b ethernet without vlan tags
    assert ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA") == 1
    assert ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB") == 1

    #12 add ipv4 protocols
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

    #13 start scenarion protocols
    ixia_instance.start_all_protocols()

    #14 create traffic item
    traffic_item3_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ipv4TrafficItem", "ipv4", traffic_item3_data) == 1

    #15 launch and stop traffic item
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    #16 check traffic item statistic, packet loss and other
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ipv4TrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    '''
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
    # Teardown
    logging.info('Broadcast test teardown')


# ------------------------test functions--------------------------

def test_l2_bridging_broadcast_core(test_l2_bridging_broadcast_fixture):
    module_manager_instance = test_l2_bridging_broadcast_fixture
    logging.info('Broadcast test core')
    t1 = 1
    t2 = 1
    assert t1 == t2