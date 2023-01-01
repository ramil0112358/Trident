from Lib.modules.Connection import Connection
from Lib.modules.Send import Send
from Lib.SystemConstants import logging_type
import logging
from datetime import datetime
import pexpect

class ModuleManager():
    '''
    Class represents basic autotest modules management.
    -Add module
    -Play module
    -Remove module
    -Change module position in playlist
    '''

    def __init__(self, topology_manager_instance):
        #for communication between modules and nodes
        self.topology_manager_instance = topology_manager_instance
        #modules dictionary contains module type as key and module instance as value
        self.module_instance_dict = {}
        #connections and they names
        self.connections = {}
        #session dictionary contains information:
        self.connect_login_sessions_dict = {}
        #connect_sessions_id_counter
        self.connect_sessions_id_counter = 0

    def show_modules(self):
        logging.info('ModuleID/ModuleType/ModuleInfo')
        for module_type, module_instance in self.module_instance_dict.items():
            if module_type == 'connect':
                logging.info(module_instance.get_id() + '/'
                                        'connect/' + module_instance.get_summary())
                if len(self.connect_login_sessions_dict) > 0:
                    for sessionID in self.connect_login_sessions_dict:
                        logging.info('established sessions: ' + sessionID)
                return 1, None
        return 0, None

    def get_sessions_dict(self):
        return self.connect_login_sessions_dict

    def login_to_node(self, args) -> bool:
        topology_name = args['topology']
        name = args['name']
        ip = args['ip']
        protocol = args['protocol']
        port = args['port']
        username = args['username']
        password = args['password']
        connection_name = args['connection_name']
        test_name = args['test_name']
        # check if node for module exist:
        topology_list = self.topology_manager_instance.get_topology_list()
        for topology in topology_list:
            if topology.get_name() == topology_name:
                logging.info("Current node list: " + str(topology.get_nodelist()))
                for node in topology.get_nodelist():
                    #logging.info("Is node.name " + node.name + ' equal to name ' + name + ' ?')
                    if node.name == name:
                        new_connection = Connection(node,
                                                    ip,
                                                    protocol,
                                                    port,
                                                    username,
                                                    password,
                                                    connection_name,
                                                    test_name)
                        self.connections[connection_name] = new_connection
                        node_type = self.topology_manager_instance.get_node_type(topology_name, name)
                        if node_type == '751048x6q':
                            if new_connection.login() == True:
                                logging.info('Connection ' + connection_name + ' successfully established')
                                return True
                            else:
                                logging.info('Connection ' + connection_name + ' failed')
                                return False
                        if node_type == '2540-48g':
                            if new_connection.login_aruba() == True:
                                logging.info('Connection ' + connection_name + ' successfully established')
                                return True
                            else:
                                logging.info('Connection ' + connection_name + ' failed')
                                return False
                logging.info('Node ' + str(name) + ' not found')
                return False
        logging.info('Topology ' + str(topology_name) + ' not found')
        return False

    def logout_node(self, connection_name):
        if connection_name in self.connections:
            self.connections[connection_name].logout()
        else:
            logging.info('Connection ' + connection_name + ' not found')

    def send_text_to_node(self, connection_name, text):
        if connection_name in self.connections:
            self.connections[connection_name].session.sendline(text)

    def wait_text_from_node(self, connection_name, text) -> bool:
        if connection_name in self.connections:
            try:
                self.connections[connection_name].session.expect(text)
                return 1
            except pexpect.TIMEOUT:
                logging.info('Expect timeout')
                return 0






