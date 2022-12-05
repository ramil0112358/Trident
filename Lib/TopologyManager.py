from Lib.Topology import Topology
from Lib.Link import Link
from Lib.SystemConstants import MAX_TOPS, devices_attr_conf_file_path, logging_type
import os.path
import logging
import time

class TopologyManager(object):
    '''
    Class represents basic topology management.
    -Remove topology
    -Save topology
    -Load topology
    -Show current topology
    -Add node to topology
    -Remove node from topology
    -Add link to topology
    -Remove link from topology
    '''
    def __init__(self, topology_list):
        self.topology_list = topology_list

    def __len__(self):
        return len(self.topology_list)

    def get_topology_list(self):
        return self.topology_list

    ##########topology methods##########
    #add topology
    def add_topology(self, args):
        name = args['topology_name']
        #Search already created topologies
        top_list_len = len(self)
        if top_list_len > 0:
            if top_list_len == MAX_TOPS:
                logging.info('Reached topology limit: ' + str(MAX_TOPS))
                return 0, None
            for topology in self.topology_list:
                if topology.name == name:
                    logging.info('topology ' + str(name) + ' already exist')
                    return 0, None
        self.topology_list.append(Topology(name))
        logging.info('topology ' + str(name) + ' successfully created')
        return 1, None

    #show current topology
    def show_topology(self, args):
        # prepare args
        name = args['topology_name']
        found_flag = False
        if len(self) > 0:
            for topology in self.topology_list:
                if topology.name == name:
                    found_flag = True
                    logging.info('Topology: ' + str(name) + '')
                    #self.visualizer.message('Object:' + str(topology), True)
                    logging.info('NodeID/Hostname/Type')
                    for node in topology.nodelist:
                        logging.info(str(node.get_id()) + ' ' +
                                     str(node.get_name()) + ' ' +
                                     str(node.get_type()))
                    logging.info('LinkID/Summary')
                    for link in topology.linklist:
                        logging.info(str(link.get_id()) + ' ' +
                                     str(link.get_summary()))
                    return 1, None
            if found_flag == False:
                logging.info('topology ' + str(name) + ' not found')
                return 0, None
        else:
            logging.info('topology ' + str(name) + ' not found')
            return 0, None

    #show topologies from projects folder
    def show_topologies(self):
        if len(self) > 0:
            for topology in self.topology_list:
                logging.info('Topology: ' + str(topology.name))
            return 1, None
        else:
            logging.info('topologies not found')
            return 0, None

    #show topologies from projects folder with links,nodes & modules
    def show_topologies_detail(self):
        if len(self) > 0:
            for topology in self.topology_list:
                logging.info('Topology: ' + str(topology.name))
                #self.visualizer.message('Topology instance:' + str(topology), True)
                logging.info('Nodes: ' + str(topology.nodelist))
                logging.info('Links: ' + str(topology.linklist))
            return 1, None
        else:
            logging.info('topologies not found')
            return 0, None

    #enter in edit topology mode
    def edit_topology(self, args):
        # prepare args
        name = args['topology_name']
        found_flag = False
        if len(self) > 0:
            for topology in self.topology_list:
                if topology.name == name:
                    found_flag = True
            if found_flag == False:
                logging.info('topology ' + str(name) + ' not found')
                return 0, None
            else:
                #return speacial code "2" for change cli mode to TOPOLOGY
                return 2, name
        else:
             logging.info('topology ' + str(name) + ' not found')
             return 0, None

    #quit from topology edit mode
    def quit_topology(self):
        return 6, None

    #remove topology
    def remove_topology(self, args):
        # prepare args
        name = args['topology_name']
        if len(self) > 0:
            for topology in self.topology_list:
                if topology.name == name:
                    self.topology_list.remove(topology)
                    logging.info('topology ' + str(name) + ' successfully removed')
                    return 1, None
            logging.info('topology not found')
            return 0, None
        else:
            logging.info('topologies not found')
            return 0, None

    ##########node methods###########

    #add new node to topology
    def add_topology_node(self, args):
        #prepare args
        hostname = args['hostname']
        type = args['type']
        topology_name = args['topology']
        # check node type
        if not os.path.isfile(devices_attr_conf_file_path + type + '.json'):
            logging.info('device type ' + type + ' not found')
            logging.info('path:' + devices_attr_conf_file_path + type + '.json')
            return 0, None
        # search demanded topology
        topology_check = False
        for topology in self.topology_list:
            if topology.name == topology_name:
                add_result = topology.add_node(hostname, type)
                if add_result == 0:
                    logging.info('node already exist')
                    return 0, None
                else:
                    logging.info('node ' + str(hostname) + ' successfully created')
                    return 1, None
        if topology_check == False:
            logging.info('topology not found')
            return 0, None

    #remove node from topology
    def remove_topology_node(self, args):
        #prepare args
        id = args['id']
        topology_name = args['topology']
        # search demanded topology
        topology_check = False
        for topology in self.topology_list:
            if topology.name == topology_name:
                remove_result = topology.remove_node(id)
                if remove_result == 0:
                    logging.info('node not found')
                    return 0, None
                else:
                    logging.info('node ' + str(id) + ' successfully removed')
                    return 1, None
        if topology_check == False:
            logging.info('topology not found')
            return 0, None

    def init_topology_node(self,
                           node_name,
                           module_manager_instance,
                           mgmt_info=None,
                           software_image_path=None,
                           new_config_path=None) -> bool:
        """
        1.Clear node's old configuration
        2.Set new management ip and default route
        3.Upgrade node's software
        4.Set new configuration
        """
        """
        First connection to node gonna be via console server.
        It creates first session with first session id in connect_login_sessions_dict dictionary.
        Thus send command to node in this method will be through module_send_send_via_hostname() 
        because this method uses first found session id for demanded hostname.
        Other commands in further part of test recommended to send via module_send_send_via_sesid() because
        one hostname can have several sessions and session id's
        """

        #Clear old configuration.Changes takes effect after reboot.
        module_manager_instance.module_send_send_via_hostname(node_name, 'copy empty-config startup-config')
        logging.info('Start reload device')
        module_manager_instance.module_send_send_via_hostname(node_name, 'reload')
        module_manager_instance.module_send_send_via_hostname(node_name, 'y')
        '''
        #
        sessions_dictionary = module_manager_instance.get_sessions_dict()
        sesid = list(sessions_dictionary.keys())[0]
        logout_args = {'connect_id': 'con1',
                       'session_id': sesid}
        module_manager_instance.module_connect_logout(logout_args)
        time.sleep(120)
        logging.info('Finish reload device')
        '''
        #Authentication again
        module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'login:')
        logging.info('Reload device complete')
        module_manager_instance.module_send_send_via_hostname(node_name, 'admin')
        module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'Password:')
        module_manager_instance.module_send_send_via_hostname(node_name, 'bulat')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'enable')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'conf t')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'int eth0')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'ip address 10.27.192.38/24')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'exit')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'ip route 0.0.0.0 0.0.0.0 10.27.192.254')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'exit')
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'wr')
        time.sleep(30)
        sessions_dictionary = module_manager_instance.get_sessions_dict()
        sesid = list(sessions_dictionary.keys())[0]
        logout_args = {'connect_id': 'con1',
                       'session_id': sesid}
        logging.info('Logout')
        module_manager_instance.module_connect_logout(logout_args)


        '''
        if mgmt info != None:
            #mgmt = [mgmt_ip, mgmt_mask, mgmt_gateway]
            mgmt_ip = mgmt_info[0]
            mgmt_mask = mgmt_info[1]
            mgmt_gateway = mgmt_info[2]
        '''
        return True





    def update_topology_node_software(self, node_name, software_image_path):
        """
        Update node software can be after management interface configuration only
        """

    def update_topology_node_config(self, new_config):
        pass

    #add link to topology
    def add_topology_link(self, args):
        #prepare args
        hostnameA = args['hostnameA']
        portA = args['portA']
        hostnameB = args['hostnameB']
        portB = args['portB']
        topology_name = args['topology']
        # search demanded topology
        topology_check = False
        for topology in self.topology_list:
            if topology.name == topology_name:
                add_result = topology.add_link(hostnameA, portA, hostnameB, portB)
                if add_result == 0:
                    logging.info('link already exist')
                    return 0, None
                else:
                    logging.info('link ' + 'id' + ' successfully created')
                    return 1, None
        if topology_check == False:
            logging.info('topology not found')
            return 0, None

    #remove link to topology
    def remove_topology_link(self, args):
        # prepare args
        id = args['id']
        topology_name = args['topology']
        # search demanded topology
        topology_check = False
        for topology in self.topology_list:
            if topology.name == topology_name:
                remove_result = topology.remove_link(id)
                if remove_result == 0:
                    logging.info('link not found')
                    return 0, None
                else:
                    logging.info('link ' + str(id) + ' successfully removed')
                    return 1, None
        if topology_check == False:
            logging.info('topology not found')
            return 0, None


