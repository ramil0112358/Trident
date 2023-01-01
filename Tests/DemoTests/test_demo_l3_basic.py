import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_B, dut_software_image_path_release
import time

#----------------------------------test l2 basic---------------------------------
'''
Cheking traffic pass through dut with routing and w/o routing.

Case1.
Topology:
192.168.1.1/24------------------------------192.168.1.2/24
IXIA[portA]-----------[xe1]DUT[xe2]-----------[portB]IXIA

Case2.
Topology:
-------192.168.2.0/24-------|--------192.168.3.0/24------
IXIA[portA].2-------.1[xe1]DUT[xe2].1-------.2[portB]IXIA

'''

# -------------------------test setup and teardown functions--------------------
@pytest.fixture
def test_demo_l3_basic_fixture(init_environment_instances):
    logging.info('Test demo l3 basic setup')
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
        "/home/ramil/PycharmProjects/trident/Tests/DemoTests/Configs/test_demo_l3_basic/test_demo_l3_basic_initial_config"
    '''
    topology_manager.init_topology_node('tr1_console',
                                        module_manager,
                                        True,  # <-clear config
                                        hostname,
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

    # Add ethernet protocols
    ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA")
    ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB")

    # Add ipv4 protocols
    assert ixia_instance.add_protocol_ipv4("Topology1",
                                           "DeviceGroupA",
                                           "192.168.1.1",
                                           "24",
                                           "192.168.1.2",
                                           False) == 1 #<--Resolve gateway

    assert ixia_instance.add_protocol_ipv4("Topology2",
                                           "DeviceGroupB",
                                           "192.168.1.2",
                                           "24",
                                           "192.168.1.1",
                                           False) == 1 #<--Resolve gateway

    # Start scenarion protocols
    ixia_instance.start_all_protocols()

    # Create traffic item
    traffic_item_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ipv4TrafficItem", "ipv4", traffic_item_data) == 1

    yield

    logging.info('Test demo l3 basic teardown')
    ixia_instance.stop_all_protocols()
    module_manager.logout_node('tr1_telnet')
    logging.info('Test demo l3 basic teardown complete')

    # ------------------------test functions--------------------------

def test_demo_l3_basic(init_environment_instances, test_demo_l3_basic_fixture):
    logging.info("Main function launch")

    core = init_environment_instances
    ixia_instance = core.ixia
    module_manager = core.module_manager

    # PartI.Check L3 traffic pass through dut w/o routing
    # Launch traffic item for 30 seconds
    '''
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ipv4TrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000
    '''
    # PartII.Check l3 traffic pass through dut with routing
    # remove ipv4 protocols without gateway resolve and set ipv4 protocols with gateway resolve
    ixia_instance.stop_all_protocols()
    ixia_instance.remove_protocol_ipv4("Topology1", "DeviceGroupA", "IPv4 1")
    ixia_instance.remove_protocol_ipv4("Topology2", "DeviceGroupB", "IPv4 2")
    time.sleep(10)
    ixia_instance.remove_protocol_ethernet("Topology1", "DeviceGroupA", "Ethernet 1")
    ixia_instance.remove_protocol_ethernet("Topology2", "DeviceGroupB", "Ethernet 2")
    time.sleep(10)

    ixia_instance.update_device_group("Topology1", "DeviceGroupA")
    ixia_instance.update_device_group("Topology2", "DeviceGroupB")

    # Add ethernet and ipv4 protocols again
    ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA")
    ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB")
    time.sleep(10)
    assert ixia_instance.add_protocol_ipv4("Topology1",
                                           "DeviceGroupA",
                                           "192.168.2.2",
                                           "24",
                                           "192.168.2.1",
                                           True) == 1  # <--Resolve gateway

    assert ixia_instance.add_protocol_ipv4("Topology2",
                                           "DeviceGroupB",
                                           "192.168.3.2",
                                           "24",
                                           "192.168.3.1",
                                           True) == 1  # <--Resolve gateway
    ixia_instance.start_all_protocols()
    login_args = {'topology': 'topology1',
                  'name': 'tr1',
                  'ip': '10.27.192.38',
                  'protocol': 'telnet',
                  'port': '23',
                  'username': 'admin',
                  'password': 'bulat',
                  'connection_name': 'tr1_telnet',
                  'test_name': 'test_demo_l3_basic'}

    ixia_instance.get_ipv4_resolve_gateway_info("Topology1", "DeviceGroupA", "IPv4 1")
    ixia_instance.get_ipv4_resolve_gateway_info("Topology2", "DeviceGroupB", "IPv4 2")


    assert module_manager.login_to_node(login_args) == 1

    # change config for route traffic
    module_manager.send_text_to_node('tr1_telnet', 'enable')
    module_manager.send_text_to_node('tr1_telnet', 'conf t')
    module_manager.send_text_to_node('tr1_telnet', 'int xe1')
    module_manager.send_text_to_node('tr1_telnet', 'no switchport')
    module_manager.send_text_to_node('tr1_telnet', 'ip address 192.168.2.1/24')
    module_manager.send_text_to_node('tr1_telnet', 'int xe2')
    module_manager.send_text_to_node('tr1_telnet', 'no switchport')
    module_manager.send_text_to_node('tr1_telnet', 'ip address 192.168.3.1/24')
    module_manager.send_text_to_node('tr1_telnet', 'exit')
    module_manager.send_text_to_node('tr1_telnet', 'wr')

    '''
    I cant delete traffic item i used before, create new one and apply changes.Ixia report error:
    ixnetwork_restpy.errors.BadRequestError:  Args do not match signature
    ../../venv/lib/python3.7/site-packages/ixnetwork_restpy/connection.py:461: BadRequestError

    I can only make old traffic item inactive -> disable it
    '''
    # ixia_instance.remove_traffic_item("ipv4TrafficItem")<--dosent work
    ixia_instance.disable_traffic_item("ipv4TrafficItem")

    traffic_item2_data = {
        "source_device_group_name": "DeviceGroupA",
        "dest_device_group_name": "DeviceGroupB",
        "framerate_type": "framesPerSecond",
        "framerate_value": "100",
        "frame_size": "1400",
        "bidir": 0,
        "control_type": "continuous"}
    assert ixia_instance.add_traffic_item("ipv4TrafficItem2", "ipv4", traffic_item2_data) == 1

    # Launch traffic item for 30 seconds
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ipv4TrafficItem2"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000