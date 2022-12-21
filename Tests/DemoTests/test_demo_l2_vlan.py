import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_B
import time

# -------------------------test setup and teardown functions--------------------
@pytest.fixture
def test_demo_l2_vlan_fixture(init_environment_instances):
    core = init_environment_instances
    topology_manager = core.topology_manager
    module_manager = core.module_manager
    # Setup section
    logging.info('Test demo l2 vlan setup')

    # Create topology
    top_args = {'topology_name': 'topology1'}
    topology_manager.add_topology(top_args)

    # Create node
    node_args = {'name': 'tr1',
                 'type': '751048x6q',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)

    # Create connection module
    connect_args = {'topology': 'topology1',
                    'name': 'tr1',
                    'ip': '10.27.193.2',
                    'protocol': 'console',
                    'port': '2037',
                    'username': 'admin',
                    'password': 'bulat'}
    module_manager.add_module_connect(connect_args)
    connect_id = module_manager.module_instance_dict['connect']
    login_args = {'connect_id': connect_id.get_id()}
    logging.debug('module_instance_dict: ' + str(module_manager.module_instance_dict))

    # Login to node
    logging.info(connect_id.get_summary())
    assert module_manager.module_connect_login(login_args) == 1

    # Init node
    hostname = "tr1"
    mgmt_info = {"ip": "10.27.192.38", "mask": "24", "gateway": "10.27.192.254"}
    dut_new_config_path = "/home/ramil/PycharmProjects/trident/Tests/DemoTests/test_demo_l2_vlan_initial_config"
    topology_manager.init_topology_node('tr1',
                                        module_manager,
                                        False,
                                        None,#hostname,
                                        None,#mgmt_info,
                                        None,#dut_software_image_path,
                                        None)#dut_new_config_path)

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

    yield

    # Teardown
    ixia_instance.stop_all_protocols()
    # Logout
    logout_args = {'connect_id': connect_id.get_id(), 'session_id': 'ses1:tr1:console:10.27.193.2:2037'}
    logout_res = module_manager.module_connect_logout(logout_args)
    logging.info('logout_res: ' + str(logout_res))
    logging.info('Test demo l2 vlan teardown complete')

    # ------------------------test functions--------------------------

def test_demo_l2_vlan(init_environment_instances, test_demo_l2_vlan_fixture):
    core = init_environment_instances
    ixia_instance = core.ixia

    # Launch traffic item for 30 seconds
    assert ixia_instance.apply_and_start_traffic_items() == 1
    time.sleep(30)
    assert ixia_instance.stop_traffic_items() == 1

    # Check traffic item statistic, packet loss.
    flow_statistics = ixia_instance.get_traffic_items_stat()
    packet_loss = flow_statistics["ethernetTrafficItem"]["Loss %"]
    logging.info("Traffic_items packet_loss: " + str(packet_loss))
    assert float(packet_loss) == 0.000


    '''
    # Get session id
    sesdict = module_manager_instance.connect_login_sessions_dict.items()
    logging.info('session_dict: ' + str(sesdict))

    # Send command via session id
    command_args = {'session_id': 'ses1:tr1:console:10.27.193.2:2037',
                    'command': 'conf t'}
    module_manager_instance.module_send_send_via_sesid(command_args)
    command_args = {'session_id': 'ses1:tr1:console:10.27.193.2:2037',
                    'command': 'vlan 100-104 bridge 1'}
    module_manager_instance.module_send_send_via_sesid(command_args)
    command_args = {'session_id': 'ses1:tr1:console:10.27.193.2:2037',
                    'command': 'wr'}
    module_manager_instance.module_send_send_via_sesid(command_args)
    '''
    '''
    # Logout
    logout_args = {'connect_id': connect_id.get_id(), 'session_id': 'ses1:tr1:console:10.27.193.2:2037'}
    logout_res = module_manager_instance.module_connect_logout(logout_args)
    logging.info('logout_res: ' + str(logout_res))
    '''