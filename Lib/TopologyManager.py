from Lib.Topology import Topology
from Lib.Link import Link
from Lib.SystemConstants import MAX_TOPS, devices_attr_conf_file_path, logging_type
import os.path
import logging
import time
import paramiko

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
                    logging.info('Topology "' + str(name) + '" already exist')
                    return 0, None
        self.topology_list.append(Topology(name))
        logging.info('Topology "' + str(name) + '" successfully created')
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
                           hostname=None,
                           mgmt_info=None,
                           software_image_path=None,
                           source_config_filepath=None) -> bool:
        """
        1.Clear node's old configuration
        2.Set new hostname
        3.Set new management ip and default route. mgmt_info = {ip:"ip",mask:"mask",gateway:"gateway"}
        4.Upgrade node's software
        5.Set new configuration

        First connection to node going to be via console server.
        It creates first session with first session id in connect_login_sessions_dict dictionary.
        Thus send command to node in this method provided through module_send_send_via_hostname() 
        because this method uses first found session id for demanded hostname.
        Other commands in further parts of test recommended to send via module_send_send_via_sesid() because
        one node have one hostname and several sessions and session id's
        """

        """###
        #Clear old configuration.Changes takes effect after reboot.
        module_manager_instance.module_send_send_via_hostname(node_name, 'copy empty-config startup-config')
        module_manager_instance.module_send_send_via_hostname(node_name, 'reload')
        module_manager_instance.module_send_send_via_hostname(node_name, 'y')
        logging.info('Clear old configuration complete')
        # device needs about 120 sec to preform standart reboot
        logging.info('Reloading device...')
        time.sleep(120)

        #here device reboots and we are waiting...

        assert module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'login:') == 1
        logging.info('Reload device complete')
        module_manager_instance.module_send_send_via_hostname(node_name, 'admin')
        assert module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'Password:') == 1
        module_manager_instance.module_send_send_via_hostname(node_name, 'bulat')
        #switch needs time to complete authentication
        time.sleep(5)
        module_manager_instance.module_send_send_via_hostname(node_name, 'enable')

        if hostname != None:
            module_manager_instance.module_send_send_via_hostname(node_name, 'conf t')
            module_manager_instance.module_send_send_via_hostname(node_name, 'hostname ' + hostname)
            module_manager_instance.module_send_send_via_hostname(node_name, 'exit')
            module_manager_instance.module_send_send_via_hostname(node_name, 'wr')
            #switch needs time to save configuration
            time.sleep(5)
            logging.info('Hostname configuration complete')

        #check if new management configuration needed
        if mgmt_info != None:
            module_manager_instance.module_send_send_via_hostname(node_name, 'conf t')
            module_manager_instance.module_send_send_via_hostname(node_name, 'int eth0')
            module_manager_instance.module_send_send_via_hostname(node_name,
                                                                  'ip address ' +
                                                                  mgmt_info["ip"] +
                                                                  '/' + mgmt_info["mask"])
            module_manager_instance.module_send_send_via_hostname(node_name, 'exit')
            module_manager_instance.module_send_send_via_hostname(node_name,
                                                                  'ip route 0.0.0.0 0.0.0.0 ' +
                                                                  mgmt_info["gateway"])
            module_manager_instance.module_send_send_via_hostname(node_name, 'exit')
            module_manager_instance.module_send_send_via_hostname(node_name, 'wr')
            #switch needs time to save configuration
            time.sleep(5)
            logging.info('Management configuration complete')

        #check if software update needed
        if software_image_path != None:
            module_manager_instance.module_send_send_via_hostname(node_name, 'copy ftp ftp://' +
                                                                  software_image_path + ' backup')
            #device needs about 120 sec to download new software image
            logging.info('Downloading image from ' + software_image_path + '...')
            time.sleep(120)
            assert module_manager_instance.module_connect_wait_text_via_hostname(node_name, hostname + '#') == 1
            logging.info('Download complete')

            module_manager_instance.module_send_send_via_hostname(node_name, 'boot backup')
            #device needs times to offer password
            time.sleep(5)
            assert module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'admin:') == 1
            module_manager_instance.module_send_send_via_hostname(node_name, 'bulat')
            #device needs times to apply new software image
            time.sleep(5)
            module_manager_instance.module_send_send_via_hostname(node_name, 'reload')
            module_manager_instance.module_send_send_via_hostname(node_name, 'y')
            #device needs about 200 sec to reload with new software image
            logging.info('Updating device...')
            time.sleep(200)

            #here device reboots and we are waiting...

            assert module_manager_instance.module_connect_wait_text_via_hostname(node_name, 'login:') == 1
            logging.info('Update complete')
        ###"""

        #check if new software update needed
        if source_config_filepath != None:
            #connect to device via sftp with paramiko
            #open a transport
            host, port = mgmt_info["ip"], 22
            transport = paramiko.Transport((host, port))

            #authentication
            username, password = "admin", "bulat"
            transport.connect(None, username, password)

            #connect
            sftp = paramiko.SFTPClient.from_transport(transport)

            '''
            #download
            filepath = "/usr/local/etc/ZebOS.conf"
            localpath = "/home/ramil/PycharmProjects/trident/RegressionTests/ZebOS.conf"
            sftp.get(filepath, localpath)
            '''

            #upload
            #convert source configuration file to list
            source_config_file = open(source_config_filepath, "r")
            source_config_file_list = source_config_file.read()
            source_config_file.close()
            #write source list to destination configuration file on device per line
            dest_config_filepath = "/usr/local/etc/ZebOS.conf"
            remote_config_file = sftp.open(dest_config_filepath, "w", -1)
            remote_config_file.writelines(source_config_file_list)
            remote_config_file.close()

            #close
            if sftp: sftp.close()
            if transport: transport.close()

        #Final reload
        #module_manager_instance.module_send_send_via_hostname(node_name, 'copy empty-config startup-config')
        #module_manager_instance.module_send_send_via_hostname(node_name, 'reload')
        #module_manager_instance.module_send_send_via_hostname(node_name, 'y')
        '''

        sessions_dictionary = module_manager_instance.get_sessions_dict()
        sesid = list(sessions_dictionary.keys())[0]
        logout_args = {'connect_id': 'con1',
                       'session_id': sesid}
        logging.info('Logout')
        module_manager_instance.module_connect_logout(logout_args)
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


