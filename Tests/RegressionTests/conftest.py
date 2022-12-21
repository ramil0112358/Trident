import pytest

#from configurator.cli import CliInputOutputManager, CliVisualizer, CommandParser
from Lib import TopologyManager
#from configurator.core import CommandExecutor, TopologyManager
from Lib.SystemConstants import global_command_set_path,global_command_set_filename
from Lib.modules import ModuleManager
#from configurator.core import Script
import logging

@pytest.fixture()
def init_environment_instances():
    topology_list = []
    topology_manager_instance = TopologyManager.TopologyManager(topology_list)
    module_manager_instance = ModuleManager.ModuleManager(topology_manager_instance)
    logging.info("Regression test conftest.py configuration complete")
    return topology_list, topology_manager_instance, module_manager_instance



