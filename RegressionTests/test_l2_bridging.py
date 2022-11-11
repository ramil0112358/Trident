import logging
import pytest
from Lib.modules.Ixia import Ixia
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
    ixia_instance.add_interface_to_scenario("1/7")
    ixia_instance.add_interface_to_scenario("2/2")
    #10.add topology to scenario
    port_list = list()
    port_list.append("1/7")
    assert ixia_instance.add_topology(port_list, "Topology1") == 1
    port_list2 = list()
    port_list2.append("2/2")
    assert ixia_instance.add_topology(port_list2, "Topology2") == 1
    assert ixia_instance.add_device_group("Topology1", "DeviceGroupA", 1) == 1
    assert ixia_instance.add_device_group("Topology2", "DeviceGroupB", 5) == 1
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

    #ixia_instance.add_traffic_item("L2", "Raw", "Data")


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
