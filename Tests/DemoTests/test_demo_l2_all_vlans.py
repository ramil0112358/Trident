import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_C, dut_software_image_path_release
import time

#----------------------------------test l2 all vlans---------------------------------
'''
Cheking of traffic pass through dut with tagged with tags 2-4093
Topology:
IXIA[portC]-----[xe1]DUT2[xe22]----[p52]A2[p1]------[portA]IXIA
'''

# -------------------------test setup and teardown functions--------------------
@pytest.fixture
def test_demo_l2_all_vlans_fixture(init_environment_instances):
    logging.info('Test demo l2 all vlans setup')
    core = init_environment_instances
    topology_manager = core.topology_manager
    module_manager = core.module_manager

    # Create topology
    top_args = {'topology_name': 'topology1'}
    topology_manager.add_topology(top_args)

    # Create nodes
    node_args = {'name': 'dut2',
                 'type': '751048x6q',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)

    node_args = {'name': 'a2',
                 'type': '2540-48g',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)

    '''
    # Create connection and login to node dut2
    login_args = {'topology': 'topology1',
                  'name': 'dut2',
                  'ip': '10.27.193.2',
                  'protocol': 'console',
                  'port': '2039',
                  'username': 'admin',
                  'password': 'bulat',
                  'connection_name': 'dut2_console',
                  'test_name': 'test_demo_l2_all_vlans'}
    assert module_manager.login_to_node(login_args) == 1

    hostname = "dut2"
    mgmt_info = {"ip": "10.27.192.39", "mask": "24", "gateway": "10.27.192.254"}
    dut_software_image_path = dut_software_image_path_release + \
                              'releases-v22.237/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.4-GA2.0-full'
    '''
    #dut_software_image_path = dut_software_image_path_release + \
    #                          'releases-v22.160/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.2-GA2.0-full'
    '''
    dut_new_config_path = \
        "/home/ramil/PycharmProjects/trident/Tests/DemoTests/Configs/test_demo_l2_all_vlans/dut2_initial_config"

    topology_manager.init_topology_node('dut2_console',
                                        module_manager,
                                        True,#<-clear config
                                        hostname,
                                        mgmt_info,
                                        None,#dut_software_image_path,
                                        dut_new_config_path,
                                        True)  # <-logout session


    # Create connection and login to node a2
    login_args = {'topology': 'topology1',
                  'name': 'a2',
                  'ip': '10.27.193.2',
                  'protocol': 'console',
                  'port': '2034',
                  'username': 'admin',
                  'password': 'bulat',
                  'connection_name': 'a2_console',
                  'test_name': 'test_demo_l2_all_vlans'}
    assert module_manager.login_to_node(login_args) == 1

    hostname_aruba = "a24"
    
    #No need to set full path to aruba config file because rest of the path 
    #configured in tftp-server configuration.Details in TopologyManager.py file
    
    source_config_filepath = 'DemoTests/Configs/test_demo_l2_all_vlans/a2_initial_config'
    topology_manager.init_topology_node_aruba('a2_console',
                                              module_manager,
                                              True,#clear_config
                                              hostname_aruba,#set_hostname
                                              source_config_filepath,
                                              True)#logout_session

    '''
    # Ixia launch
    ixia_instance = Ixia("10.27.152.3", "11009", "admin", "admin")
    core.ixia = ixia_instance
    ixia_ixnetwork = ixia_instance.get_ixnetwork_instance()

    # init new scenario with ports(
    ixia_instance.add_scenario()
    ixia_instance.add_interface_to_scenario(PORT_A)
    ixia_instance.add_interface_to_scenario(PORT_C)

    # Add topology to scenario
    port_list = list()
    port_list.append(PORT_A)
    assert ixia_instance.add_topology(port_list, "Topology1") == 1
    port_list2 = list()
    port_list2.append(PORT_C)
    assert ixia_instance.add_topology(port_list2, "Topology2") == 1
    assert ixia_instance.add_device_group("Topology1",
                                          "DeviceGroupA",
                                          254  # <- devicr group multiplier(amount of hosts)
                                          ) == 1
    assert ixia_instance.add_device_group("Topology2",
                                          "DeviceGroupB",
                                          254  # <- devicr group multiplier(amount of hosts)
                                          ) == 1
    # Add protocol ethernet
    vlan_start_value = "3764"
    assert ixia_instance.add_protocol_ethernet("Topology1",
                                               "DeviceGroupA",
                                               True,  # <- enable vlan tagging
                                               1,  # <- amount of vlan tags
                                               vlan_start_value) == 1

    vlan_start_value = "3764"
    assert ixia_instance.add_protocol_ethernet("Topology2",
                                               "DeviceGroupB",
                                               True,  # <- enable vlan tagging
                                               1,  # <- amount of vlan tags
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


    tracking = ixia_instance.traffic_items[-1].Tracking.fing()
    logging.info('Tracking: ' + tracking)
    logging.info('Trackby: ' + tracking.TrackBy)


    logging.info('Test demo l2 all vlans setup complete')

    yield

    logging.info('Test demo l2 all vlans teardown')
    #module_manager.logout_node('dut2_console')
    #module_manager.logout_node('a2_console')
    logging.info('Test demo l2 all vlans teardown complete')

def test_demo_l2_all_vlans(init_environment_instances, test_demo_l2_all_vlans_fixture):
    logging.info("Main function launch")
    pass

    core = init_environment_instances
    ixia_instance = core.ixia
    module_manager = core.module_manager

    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    logging.info("Flow statistics: " + str(flow_statistics))
    packet_loss = flow_statistics["ethernetTrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000
