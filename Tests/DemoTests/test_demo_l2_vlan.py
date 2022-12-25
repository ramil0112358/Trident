import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_B, dut_software_image_path_release
import time

# -------------------------test setup and teardown functions--------------------
@pytest.fixture
def test_demo_l2_vlan_fixture(init_environment_instances):
    logging.info('Test demo l2 vlan setup')
    core = init_environment_instances
    topology_manager = core.topology_manager
    module_manager = core.module_manager

    # Create topology
    top_args = {'topology_name': 'topology1'}
    topology_manager.add_topology(top_args)

    # Create node
    node_args = {'name': 'tr1',
                 'type': '751048x6q',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)

    # Create connection and login to node
    login_args = {'topology': 'topology1',
                    'name': 'tr1',
                    'ip': '10.27.193.2',
                    'protocol': 'console',
                    'port': '2037',
                    'username': 'admin',
                    'password': 'bulat',
                    'connection_name': 'tr1_console',
                    'test_name': 'test_demo_l2_vlan'}
    assert module_manager.login_to_node(login_args) == 1

    # Init node
    hostname = "tr1"
    mgmt_info = {"ip": "10.27.192.38", "mask": "24", "gateway": "10.27.192.254"}
    #dut_software_image_path = dut_software_image_path_release + \
    #                          'releases-v22.237/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.4-GA2.0-full'
    dut_software_image_path = dut_software_image_path_release + \
                              'releases-v22.160/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.2-GA2.0-full'

    dut_new_config_path = \
        "/home/ramil/PycharmProjects/trident/Tests/DemoTests/Configs/test_demo_l2_vlan/test_demo_l2_vlan_initial_config"

    '''
    topology_manager.init_topology_node('tr1_console',
                                        module_manager,
                                        False,#<-clear config
                                        None,#hostname,
                                        None,#mgmt_info,
                                        None,#dut_software_image_path,
                                        None,#dut_new_config_path)
                                        False)#<-logout session
    '''
    topology_manager.init_topology_node('tr1_console',
                                 module_manager,
                                 False,#True,  # <-clear config
                                 None,#hostname,
                                 mgmt_info,
                                 None,#dut_software_image_path,
                                 dut_new_config_path,
                                 True)  # <-logout session

    '''
    # Ixia launch
    ixia_instance = Ixia("10.27.152.3", "11009", "admin", "admin")
    core.ixia = ixia_instance
    ixia_ixnetwork = ixia_instance.get_ixnetwork_instance()

    # init new scenario with ports(
    ixia_instance.add_scenario()
    ixia_instance.add_interface_to_scenario(PORT_A)
    ixia_instance.add_interface_to_scenario(PORT_B)

    # Add topology to scenario
    port_list = list()
    port_list.append(PORT_A)
    assert ixia_instance.add_topology(port_list, "Topology1") == 1
    port_list2 = list()
    port_list2.append(PORT_B)
    assert ixia_instance.add_topology(port_list2, "Topology2") == 1
    assert ixia_instance.add_device_group("Topology1",
                                          "DeviceGroupA",
                                          1 #<- devicr group multiplier(amount of hosts)
                                          ) == 1
    assert ixia_instance.add_device_group("Topology2",
                                          "DeviceGroupB",
                                          1 #<- devicr group multiplier(amount of hosts)
                                          ) == 1
    # Add protocol ethernet
    vlan_start_value = "100"
    assert ixia_instance.add_protocol_ethernet("Topology1",
                                               "DeviceGroupA",
                                               True, #<- enable vlan tagging
                                               1,    #<- amount of vlan tags should be equal to amount of hosts
                                               vlan_start_value) == 1

    vlan_start_value = "100"
    assert ixia_instance.add_protocol_ethernet("Topology2",
                                               "DeviceGroupB",
                                               True, #<- enable vlan tagging
                                               1,    #<- amount of vlan tags should be equal to amount of hosts
                                               vlan_start_value) == 1

    # Start protocols
    ixia_instance.start_all_protocols()

    # Add traffic item
    traffic_item1_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ethernetTrafficItem", "ethernetVlan", traffic_item1_data) == 1
    '''



    yield

    '''
    # Teardown
    ixia_instance.stop_all_protocols()
    # Logout
    logout_args = {'connect_id': connect_id.get_id(), 'session_id': 'ses1:tr1:console:10.27.193.2:2037'}
    logout_res = module_manager.module_connect_logout(logout_args)
    sessions_dictionary = module_manager.get_sessions_dict()
    sesid = list(sessions_dictionary.keys())[0]
    logout_args = {'connect_id': 'con1',
                   'session_id': sesid}
    '''



    logging.info('Test demo l2 vlan teardown complete')

    # ------------------------test functions--------------------------

def test_demo_l2_vlan(init_environment_instances, test_demo_l2_vlan_fixture):
    logging.info("main function launch")

    '''
    core = init_environment_instances
    ixia_instance = core.ixia
    module_manager = core.module_manager

    # Launch traffic item for 30 seconds
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ethernetTrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    #assert float(packet_loss) == 0.000

    #remove ethernet protocols with vlan tag and set ethernet protocol w/o vlan tagging
    ixia_instance.remove_protocol_ethernet("Topology1", "DeviceGroupA", "Ethernet 1")
    ixia_instance.remove_protocol_ethernet("Topology2", "DeviceGroupB", "Ethernet 2")

    ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA")
    ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB")

    # Get session id
    sesdict = module_manager.connect_login_sessions_dict.items()
    logging.info('session_dict: ' + str(sesdict))
   
    # Send command via session id
    sesid = list(sesdict.keys())[0]
    logging.info('session_id: ' + str(sesid))
    assert module_manager.send_command_via_sesid(sesid, 'conf t') == 1
    module_manager.send_command_via_sesid(sesid, 'int xe1-2')
    module_manager.send_command_via_sesid(sesid, 'switchport mode access')
    module_manager.send_command_via_sesid(sesid, 'switchport access vlan 100')
    module_manager.send_command_via_sesid(sesid, 'exit')
    module_manager.send_command_via_sesid(sesid, 'wr')

    #remove old traffic item and set new for new ethernet protcols
    ixia_instance.remove_traffic_item("ethernetTrafficItem")

    traffic_item2_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ethernetTrafficItem2", "ethernetVlan", traffic_item2_data) == 1

    # Launch traffic item for 30 seconds
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ethernetTrafficItem2"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000
    '''








