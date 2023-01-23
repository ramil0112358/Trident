import os.path
import logging
import time
import paramiko
import subprocess
from Lib.Topology import Topology
from Lib.SystemConstants import MAX_TOPS, \
                                devices_attr_conf_file_path, \
                                autotest_system_server_ip

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
        name = args['name']
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
                add_result = topology.add_node(name, type)
                if add_result == 0:
                    logging.info('node already exist')
                    return 0, None
                else:
                    logging.info('node ' + str(name) + ' successfully created')
                    return 1, None
        if topology_check == False:
            logging.info('topology not found')
            return 0, None

    def get_node_type(self, topology_name, topology_node_name):
        target_topology = False
        for topology in self.topology_list:
            if topology.name == topology_name:
                target_topology = topology
                break
        if target_topology == False:
            logging.info('Topology + ' + topology_name + ' not found')
            return 0
        target_node = False
        for node in target_topology.nodelist:
            if node.get_name() == topology_node_name:
                return node.get_type()
        if target_node == False:
            logging.info('Node + ' + topology_node_name + ' not found')
            return 0

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

    def authenticate_node(self, module_manager, connection_name):
        assert module_manager.wait_text_from_node(connection_name, 'login:') == 1
        module_manager.send_text_to_node(connection_name, 'admin')
        assert module_manager.wait_text_from_node(connection_name, 'Password:') == 1
        module_manager.send_text_to_node(connection_name, 'bulat')
        # switch needs time to complete authentication
        time.sleep(5)
        module_manager.send_text_to_node(connection_name, 'enable')

    def init_topology_node(self,
                           connection_name,
                           module_manager,
                           clear_config=True,
                           hostname=None,
                           mgmt_info=None,
                           software_image_path=None,
                           source_config_filepath=None,
                           logout=False) -> bool:
        """
        1.Clear node's old configuration
        2.Set new hostname
        3.Set new management ip and default route. mgmt_info = {ip:"ip",mask:"mask",gateway:"gateway"}
        4.Upgrade node's software
        5.Set new configuration
        6.Logout

        First connection to node going to be via console server.
        It creates first session with first session id in connect_login_sessions_dict dictionary.
        Thus send command to node in this method provided through module_send_send_via_hostname() 
        because this method uses first found session id for demanded hostname.
        Other commands in further parts of test recommended to send via module_send_send_via_sesid() because
        one node have one hostname and several sessions and session id's
        """

        if clear_config == True:
            #clear old configuration.Changes takes effect after reboot.
            module_manager.send_text_to_node(connection_name, 'copy empty-config startup-config')
            module_manager.send_text_to_node(connection_name, 'reload')
            module_manager.send_text_to_node(connection_name, 'y')

            logging.info('Clear old configuration complete')
            #device needs about 120 sec to perform standart reboot
            logging.info('Reloading device...')
            time.sleep(120)

            #here device reboots and we are waiting...

            self.authenticate_node(module_manager, connection_name)
            logging.info('Reload device complete')

        if hostname != None:
            module_manager.send_text_to_node(connection_name, 'conf t')
            module_manager.send_text_to_node(connection_name, 'hostname ' + hostname)
            module_manager.send_text_to_node(connection_name, 'exit')
            module_manager.send_text_to_node(connection_name, 'wr')

            #switch needs time to save configuration
            time.sleep(5)
            logging.info('Hostname configuration complete')

        #check if new management configuration needed
        if mgmt_info != None:
            module_manager.send_text_to_node(connection_name, 'conf t')
            module_manager.send_text_to_node(connection_name, 'int eth0')
            module_manager.send_text_to_node(connection_name, 'ip address ' + mgmt_info["ip"] + '/' + mgmt_info["mask"])
            module_manager.send_text_to_node(connection_name, 'exit')
            module_manager.send_text_to_node(connection_name, 'ip route 0.0.0.0 0.0.0.0 ' + mgmt_info["gateway"])
            module_manager.send_text_to_node(connection_name, 'exit')
            module_manager.send_text_to_node(connection_name, 'wr')
            #switch needs time to save configuration
            time.sleep(5)
            logging.info('Management configuration complete')

        #check if software update needed
        if software_image_path != None:
            module_manager.send_text_to_node(connection_name, 'copy ftp ftp://' + software_image_path + ' backup')
            #device needs about 120 sec to download new software image
            logging.info('Downloading image from ' + software_image_path + '...')
            time.sleep(120)
            assert module_manager.wait_text_from_node(connection_name, hostname + '#') == 1
            logging.info('Download complete')

            module_manager.send_text_to_node(connection_name, 'boot backup')
            #device needs times to offer password
            time.sleep(5)
            assert module_manager.wait_text_from_node(connection_name, 'admin:') == 1
            module_manager.send_text_to_node(connection_name, 'bulat')
            #device needs times to apply new software image
            time.sleep(5)
            module_manager.send_text_to_node(connection_name, 'reload')
            module_manager.send_text_to_node(connection_name, 'y')
            #device needs about 200 sec to reload with new software image
            logging.info('Updating device...')
            time.sleep(200)

            #here device reboots and we are waiting...

            self.authenticate_node(module_manager, connection_name)
            logging.info('Update complete')

        #check if config update needed
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

            module_manager.send_text_to_node(connection_name, 'reload')
            module_manager.send_text_to_node(connection_name, 'y')
            # device needs about 120 sec to perform standart reboot
            logging.info('Updateing device config...')
            time.sleep(120)

            # here device reboots and we are waiting...

            self.authenticate_node(module_manager, connection_name)
            logging.info('Config update complete')

        if logout == True:
            module_manager.logout_node(connection_name)

        return True

    def authenticate_node_aruba(self, module_manager, connection_name):
        # "double enter" invintation
        module_manager.send_text_to_node(connection_name, '\r\n')
        time.sleep(5)
        module_manager.send_text_to_node(connection_name, '\r\n')
        time.sleep(15)
        # "press any key to continue" invintation
        module_manager.send_text_to_node(connection_name, '\r\n')
        time.sleep(15)
        module_manager.send_text_to_node(connection_name, 'enable')
        assert module_manager.wait_text_from_node(connection_name, '#') == 1

    def init_topology_node_aruba(self,
                                 connection_name,
                                 module_manager,
                                 clear_config=True,
                                 hostname=None,
                                 source_config_filepath=None,
                                 logout=False) -> bool:


        if clear_config == True:
            # clear old configuration.Changes takes effect after reboot.
            module_manager.send_text_to_node(connection_name, 'erase startup-config')
            module_manager.send_text_to_node(connection_name, 'y')

            logging.info('Clear old configuration complete')
            # device needs about 50 sec to perform standart reboot
            logging.info('Reloading device...')
            time.sleep(50)

            # here device reboots and we are waiting...

            self.authenticate_node_aruba(module_manager, connection_name)
            logging.info('Reload device complete')

        if hostname != None:
            module_manager.send_text_to_node(connection_name, 'conf t')
            module_manager.send_text_to_node(connection_name, 'hostname ' + hostname)
            module_manager.send_text_to_node(connection_name, 'exit')
            module_manager.send_text_to_node(connection_name, 'write memory')

            #switch needs time to save configuration
            time.sleep(5)
            logging.info('Hostname configuration complete')

        # check if config update needed
        if source_config_filepath != None:
            '''
            Tftp server "tftpy" have two disadvantages
            -server.listen method makes infinite loop which blocks further python script execution
            -socket bind with port number < 1024 requres root user level
            so standart tftp application for linux will be used.
            '''
            #server = tftpy.TftpServer(filepath)
            #server.listen('0.0.0.0', 69)
            '''
            installation: sudo apt install tftpd-hpa
            configuration: sudo nano /etc/default/tftpd-hpa
            launch: systemctl restart tftpd-hpa
            
            # /etc/default/tftpd-hpa

            TFTP_USERNAME="tftp"
            TFTP_DIRECTORY="/home/ramil/PycharmProjects/trident/Tests/"
            TFTP_ADDRESS="10.27.152.7:69"
            TFTP_OPTIONS="--secure"
            '''

            #tftp server running check
            '''
            out = subprocess.call("systemctl | grep tftpd-hpa.service")
            output = out.read()
            logging.info("output: " + output)
            '''

            #cofnigure management ip address
            module_manager.send_text_to_node(connection_name, 'conf t')
            module_manager.send_text_to_node(connection_name, 'int vlan 1')
            module_manager.send_text_to_node(connection_name, 'ip address 10.27.192.38/24')
            module_manager.send_text_to_node(connection_name, 'exit')
            module_manager.send_text_to_node(connection_name, 'ip route ' + autotest_system_server_ip + '/32 ' + '10.27.192.254')
            module_manager.send_text_to_node(connection_name, 'exit')


            module_manager.send_text_to_node(connection_name,'copy tftp startup-config ' +
                                             autotest_system_server_ip + ' ' + source_config_filepath)
            time.sleep(5)
            module_manager.send_text_to_node(connection_name, 'y')
            logging.info('Updateing device config...')
            time.sleep(50)

            # here device reboots and we are waiting...

            logging.info('Config update complete')

        if logout == True:
            module_manager.logout_node(connection_name)

        return True




    '''
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
    '''


