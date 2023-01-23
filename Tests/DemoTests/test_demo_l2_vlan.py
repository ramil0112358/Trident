import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_B, dut_software_image_path_release
import time

#----------------------------------test l2 vlan---------------------------------
'''
Cheking of traffic pass through dut with tagged and untagged frames
Topology:
IXIA[portA]-----------[xe1]DUT[xe2]----------[portB]IXIA
'''

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
                                        True,  # <-clear config
                                        hostname,
                                        mgmt_info,
                                        dut_software_image_path,
                                        dut_new_config_path,
                                        True)  # <-logout session



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
                                               1,    #<- amount of vlan tags
                                               vlan_start_value) == 1

    vlan_start_value = "100"
    assert ixia_instance.add_protocol_ethernet("Topology2",
                                               "DeviceGroupB",
                                               True, #<- enable vlan tagging
                                               1,    #<- amount of vlan tags
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
    logging.info('Test demo l2 vlan setup complete')


    yield

    logging.info('Test demo l2 vlan teardown')

    ixia_instance.stop_all_protocols()

    module_manager.logout_node('tr1_telnet')
    logging.info('Test demo l2 vlan teardown complete')


    # ------------------------test functions--------------------------

def test_demo_l2_vlan(init_environment_instances, test_demo_l2_vlan_fixture):
    logging.info("Main function launch")

    core = init_environment_instances
    ixia_instance = core.ixia
    module_manager = core.module_manager

    # PartI.Check taged traffic pass through dut
    # Launch traffic item for 30 seconds
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ethernetTrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000


    #PartII.Check untag traffic pass through dut
    #remove ethernet protocols with vlan tag and set ethernet protocol w/o vlan tagging
    ixia_instance.remove_protocol_ethernet("Topology1", "DeviceGroupA", "Ethernet 1")
    ixia_instance.remove_protocol_ethernet("Topology2", "DeviceGroupB", "Ethernet 2")

    ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA")
    ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB")



    login_args = {'topology': 'topology1',
                  'name': 'tr1',
                  'ip': '10.27.192.38',
                  'protocol': 'telnet',
                  'port': '23',
                  'username': 'admin',
                  'password': 'bulat',
                  'connection_name': 'tr1_telnet',
                  'test_name': 'test_demo_l2_vlan'}
    assert module_manager.login_to_node(login_args) == 1

    #change config for untag traffic
    module_manager.send_text_to_node('tr1_telnet', 'int xe1-2')
    module_manager.send_text_to_node('tr1_telnet', 'switchport mode access')
    module_manager.send_text_to_node('tr1_telnet', 'switchport access vlan 100')
    module_manager.send_text_to_node('tr1_telnet', 'exit')
    module_manager.send_text_to_node('tr1_telnet', 'wr')


    '''
    I cant delete traffic item i used before, create new one and apply changes.Ixia report error:
    ixnetwork_restpy.errors.BadRequestError:  Args do not match signature
../../venv/lib/python3.7/site-packages/ixnetwork_restpy/connection.py:461: BadRequestError

    I can only make old traffic item inactive -> disable it
    '''


    #ixia_instance.remove_traffic_item("ethernetTrafficItem")<--dosent work
    ixia_instance.disable_traffic_item("ethernetTrafficItem")

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










