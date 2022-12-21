import pytest
from Lib import TopologyManager
from Lib.modules import ModuleManager
import logging

class Core:
    pass

@pytest.fixture()
def init_environment_instances():
    topology_list = []
    Core.ixia = None
    Core.topology_list = topology_list
    Core.topology_manager = TopologyManager.TopologyManager(topology_list)
    Core.module_manager = ModuleManager.ModuleManager(Core.topology_manager)
    logging.info("Demo test conftest.py configuration complete")
    return Core



