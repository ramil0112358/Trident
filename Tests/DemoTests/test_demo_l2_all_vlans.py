import logging
import pytest
from Lib.modules.Ixia import Ixia
from Lib.SystemConstants import PORT_A, PORT_B, dut_software_image_path_release
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
    '''
    # Create nodes
    node_args = {'name': 'dut2',
                 'type': '751048x6q',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)
    '''
    # Create nodes
    node_args = {'name': 'a2',
                 'type': '2540-48g',
                 'topology': 'topology1'}
    topology_manager.add_topology_node(node_args)

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

    source_config_filepath = \
        '/home/ramil/PycharmProjects/trident/Tests/DemoTests/Configs/test_demo_l2_all_vlans/test_demo_l2_all_vlans_a2_initial_config'
    topology_manager.init_topology_node_aruba('a2_console',
                                              module_manager,
                                              True,#clear_config
                                              None,#set_hostname
                                              source_config_filepath,
                                              True)#logout_session

    yield

    module_manager.logout_node('a2_console')

def test_demo_l2_all_vlans(init_environment_instances, test_demo_l2_all_vlans_fixture):
    logging.info("Main function launch")
    pass