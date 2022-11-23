from Lib.Topology import Topology
from Lib.Link import Link
from Lib.SystemConstants import MAX_TOPS, devices_attr_conf_file_path, logging_type
import os.path
import logging

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


