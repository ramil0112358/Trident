from Lib.modules.Connect import Connect
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
        #connect modules id counter
        self.connect_module_id_counter = 0
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

    def add_module_connect(self, args):
        #prepage args
        #self.visualizer.message(args, True)
        topology_name = args['topology']
        hostname = args['hostname']
        ip = args['ip']
        protocol = args['protocol']
        port = args['port']
        username = args['username']
        password = args['password']
        #check if node for module exist:
        topology_list = self.topology_manager_instance.get_topology_list()
        for topology in topology_list:
            if topology.get_name() == topology_name:
                for node in topology.get_nodelist():
                    if node.hostname == hostname:
                        self.connect_module_id_counter += 1
                        new_connect = Connect(node, ip, protocol, port,
                                              username, password, self.connect_module_id_counter)
                        self.module_instance_dict['connect'] = new_connect
                        #pdb.set_trace()
                        logging.info('connection successfully added. connectionID:' +
                                                str(new_connect.get_id()))
                        #self.visualizer.message('self.module_instance_dict[connect]:' +
                        #                        str(self.module_instance_dict['connect']), logging_type)
                        return 1, None
                logging.info('node '+ str(hostname) + ' not found')
                return 0, None
        logging.info('topology ' + str(topology_name) + ' not found')
        return 0, None

    def module_connect_login(self, args):
        connect_id = args['connect_id']
        first_connection_flag = False
        connection_module_found_flag = False
        result = 0
        for module_type, module_instance in self.module_instance_dict.items():
            if module_type == 'connect':
                if connect_id == module_instance.get_id():
                    connection_module_found_flag = True
                    logging.info('login with: ' + str(connect_id) + ' connect module')
                    login_result_dict = module_instance.login()
                    login_result = login_result_dict["login_result"]
                    if login_result != False:
                        # "send" class instance init to send messages if it first login
                        if len(self.connect_login_sessions_dict) == 0:
                            first_connection_flag = True
                        # get hostname of node
                        hostname = module_instance.get_nodename()
                        # generate session id
                        self.connect_sessions_id_counter += 1
                        sesid = 'ses' + str(self.connect_sessions_id_counter) + ":" + \
                                hostname + ":" + \
                                str(login_result_dict["protocol"]) + ":" + \
                                str(login_result_dict["ip"]) + ":" + \
                                str(login_result_dict["port"])
                        # set data to session_dict
                        session_instance = login_result_dict["session_instance"]
                        self.connect_login_sessions_dict[sesid] = session_instance
                        logging.info('connection established, sessionID: ' + str(sesid))
                        # logging session
                        now = datetime.now()
                        current_datetime = now.strftime("%d%m%Y_%H:%M:%S")
                        log_filename = "/home/ramil/PycharmProjects/trident_logs/" + \
                                       str(sesid) + "_" + str(current_datetime) + ".log"
                        #log_filename = "/home/ramil/PycharmProjects/trident_logs/" + \
                         #              str(sesid) + ":" + ".log"

                        fout = open(log_filename, "wb+")
                        session_instance.logfile = fout
                        logging.info('log session ' + str(sesid) + ' to file ' + log_filename)
                        logging.debug(self.connect_login_sessions_dict)
                        result = 1
                    else:
                        logging.info('Connection failed.')
                        result = 0

        if connection_module_found_flag == False:
            logging.info('Connection module' + str(connect_id) + 'not found.')
            return 0

        if result == 1 and first_connection_flag == True:
            self.module_instance_dict['send'] = Send(self.connect_login_sessions_dict)
        return result

    def module_connect_logout(self, args):
        connect_id = args['connect_id']
        logout_session_id = args['session_id']
        # search connect module
        for module_type, module_instance in self.module_instance_dict.items():
            if module_type == 'connect':
                if connect_id == module_instance.get_id():
                    # search session
                    for session_id, session_instance in self.connect_login_sessions_dict.items():
                        if session_id == logout_session_id:
                            result = module_instance.logout(session_instance)
                            if result == True:
                                logging.info('SessionID: ' + logout_session_id +
                                                        ' successfully disconnected')
                                return 1, None
                    logging.info('SessionID: ' + logout_session_id + ' not found')
                    return 0, None
        logging.info('ConnectionID: ' + connect_id + ' not found')
        return 0, None

    #def module_connect_nodecheck(self, args):

    def module_send_send_via_sesid(self, args):
        sesID = args['session_id']
        command = args['command']
        command = command.replace('_',' ')
        # check demanded session existance
        if sesID in self.connect_login_sessions_dict:
            target_session = self.connect_login_sessions_dict[sesID]
            #print(self.module_instance_dict)
            # check send instance existance
            if 'send' in self.module_instance_dict:
                result = self.module_instance_dict['send'].send_command(target_session, command)
                if result == True:
                    return 1, None
                else:
                    return 0, None
            else:
                logging.info('At least one login should be made')
                return 0, None
        else:
            logging.info('SessionID: ' + str(sesID) + ' not found')
            return 0, None
    '''
    def module_send_send_char_via_sesid(self, args):
        sesID = args['session_id']
        char = args['char']
        char = char.replace('_', ' ')
        # check demanded session existance
        if sesID in self.connect_login_sessions_dict:
            target_session = self.connect_login_sessions_dict[sesID]
            # print(self.module_instance_dict)
            # check send instance existance
            if 'send' in self.module_instance_dict:
                result = self.module_instance_dict['send'].send_char(target_session, char)
                if result == True:
                    return 1, None
                else:
                    return 0, None
            else:
                logging.info('At least one login should be made')
                return 0, None
        else:
            logging.info('SessionID: ' + str(sesID) + ' not found')
            return 0, None
    '''

    #send command via first found session id for demanded hostname
    def module_send_send_via_hostname(self,
                                      receiver_hostname,
                                      command):
        #command = command.replace('_', ' ')
        for sessionID, session_instance in self.connect_login_sessions_dict.items():
            hostname = sessionID.split(":")[1]
            if hostname == receiver_hostname:
                if 'send' in self.module_instance_dict:
                    target_session = session_instance
                    result = self.module_instance_dict['send'].send_command(target_session, command)
                    if result == True:
                        return 1, None
                    else:
                        return 0, None
                else:
                    logging.info('At least one login should be made')
                    return 0, None
            else:
                logging.info('Hostname: ' + str(receiver_hostname) + ' not found')
        return 0, None

    # wait test via first found session id for demanded hostname
    def module_send_wait_text_via_sesid(self, args):
        sesid = args['sessionID']
        text = args['text']

        if sesid in self.connect_login_sessions_dict:
            session_instance = self.connect_login_sessions_dict[sesid]
            session_instance.expect(text)
            return 1
        else:
            logging.info('SessionID: ' + sesid + ' not found')
            return 0

    def module_connect_wait_text_via_hostname(self, hostname_text_sender, text):
        for sessionID, session_instance in self.connect_login_sessions_dict.items():
            hostname = sessionID.split(":")[1]
            if hostname == hostname_text_sender:
                if 'send' in self.module_instance_dict:
                    try:
                        session_instance.expect(text)
                        return 1
                    except pexpect.TIMEOUT:
                        logging.info('Expect timeout')
                        return 0
                else:
                    logging.info('At least one login should be made')
                    return 0
            else:
                logging.info('Hostname: ' + str(hostname_text_sender) + ' not found')
        return 0


    def add_module_ixia(self, args):
        pass

