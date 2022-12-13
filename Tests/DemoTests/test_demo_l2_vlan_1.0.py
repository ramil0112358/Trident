import logging
import pytest
from Lib.modules.Ixia import Ixia

# ------------------------init functions--------------------------
@pytest.fixture
def init_test_environment(init_environment_instances):
    topology_list, \
    topology_manager_instance, \
    module_manager_instance = init_environment_instances
    return topology_list, \
           topology_manager_instance, \
           module_manager_instance


# -------------------------test setup and teardown functions--------------------
@pytest.fixture
def test_demo_fixture(init_test_environment):
    topology_list, topology_manager_instance, module_manager_instance = init_test_environment
    # Setup section
    logging.info('Test demo l2 vlan setup')

    # 1.Create topology
    top_args = {'topology_name': 'topology1'}
    topology_manager_instance.add_topology(top_args)

    # 2.Create node
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

    # 3.Create connection module
    module_manager_instance.add_module_connect(connect_args)
    connect_id = module_manager_instance.module_instance_dict['connect']
    login_args = {'connect_id': connect_id.get_id()}
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))

    # 4.Login to node
    logging.info(connect_id.get_summary())
    assert module_manager_instance.module_connect_login(login_args) == 1

    # 4a.Init node
    hostname = "TR1"
    mgmt_info = {"ip": "10.27.192.38", "mask": "24", "gateway": "10.27.192.254"}
    software_image_path = "10.121.0.147/RZN_SWITCHES/distrib/releases-v22.237/bulat-bs7510-48x6q/bulat-bs7510-48x6q_7.1.1.0.2.0.4-GA2.0-full"
    new_config_path = "/Tests/RegressionTests/demo_config"
    topology_manager_instance.init_topology_node('node1',
                                                 module_manager_instance,
                                                 hostname,
                                                 mgmt_info,
                                                 None,#software_image_path,
                                                 None)#new_config_path)

    # 5.Get session id
    sesdict = module_manager_instance.connect_login_sessions_dict.items()
    logging.debug('session_dict: ' + str(sesdict))
    logging.debug('module_instance_dict: ' + str(module_manager_instance.module_instance_dict))

    # 6.Send command via session id
    command1_args = {'session_id': 'ses1:node1:telnet:10.27.192.38:23',
                     'command': 'conf t'}
    module_manager_instance.module_send_send_via_sesid(command1_args)
    command2_args = {'session_id': 'ses1:node1:telnet:10.27.192.38:23',
                     'command': 'vlan 778 bridge 1'}
    module_manager_instance.module_send_send_via_sesid(command2_args)

    # 7 Logout
    logout_args = {'connect_id': connect_id.get_id(), 'session_id': 'ses1:node1:telnet:10.27.192.38:23'}
    logout_res, nope = module_manager_instance.module_connect_logout(logout_args)
    logging.info('logout_res: ' + str(logout_res))

    # 8.Ixia launch
    ixia_instance = Ixia("10.27.152.3", "11009", "admin", "admin")
    ixia_ixnetwork = ixia_instance.get_ixnetwork_instance()

    # 9.init new scenario with ports(
    ixia_instance.add_scenario()
    ixia_instance.add_interface_to_scenario("2/5")
    ixia_instance.add_interface_to_scenario("2/2")

    # 10.add topology to scenario
    port_list = list()
    port_list.append("2/5")
    assert ixia_instance.add_topology(port_list, "Topology1") == 1
    port_list2 = list()
    port_list2.append("2/2")
    assert ixia_instance.add_topology(port_list2, "Topology2") == 1
    assert ixia_instance.add_device_group("Topology1", "DeviceGroupA", 1) == 1
    assert ixia_instance.add_device_group("Topology2", "DeviceGroupB", 1) == 1

    # 11.add protocol ethernet
    vlan_start_value = "100"
    assert ixia_instance.add_protocol_ethernet("Topology1", "DeviceGroupA", True, 5, vlan_start_value) == 1

    vlan_start_value = "100"
    assert ixia_instance.add_protocol_ethernet("Topology2", "DeviceGroupB", True, 5, vlan_start_value) == 1
