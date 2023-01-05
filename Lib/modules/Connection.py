import pexpect
import logging
import time
import psutil
import json
from Lib.SystemConstants import devices_attr_conf_file_path, connections_log_path
import signal
'''
Class represents connect and 
disconnect actions for Node.
'''
class Connection():

    def __init__(self,
                 node,
                 ip,
                 protocol,
                 port,
                 username,
                 password,
                 connection_name,
                 test_name):

        self.node = node
        self.ip = ip
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.connection_name = connection_name
        self.test_name = test_name
        logging.info("Connection " + connection_name + " ready")

    def get_nodename(self):
        return self.node.get_name()

    def get_summary(self):
        return str(self.protocol) + ' ' + \
               str(self.ip) + ':' + \
               str(self.port) + ' ' + \
               str(self.username) + '/' + \
               str(self.password)

    def login(self):
        result = False
        #get node type specific attributes from json library
        device_attr_json = devices_attr_conf_file_path + str(self.node.get_type()) + '.json'
        logging.info("device_attr_json: " + device_attr_json)
        with open(device_attr_json, "r") as read_file:
            node_attributes = json.load(read_file)
        for item in node_attributes.keys():
            setattr(self, item, node_attributes[item])

        if self.protocol == 'telnet' or self.protocol == 'console':
            try:
                credentials = 'telnet ' + str(self.ip) + ' ' + str(self.port)
                self.session = pexpect.spawn(credentials, timeout=30)
                logging.debug('session begin')
                time.sleep(5)
                logging.debug('5 sec pass')
                # telnet connection over console server
                if self.protocol == 'console':
                    logging.debug('console pass')
                    # if remote device refuses connection session process terminates immediately
                    # check session process existence
                    if psutil.pid_exists(self.session.pid) == False:
                        logging.info('Device {host} connection refused.'.format(host=str(self.ip)))
                        return False
                    # connection to device console port via telnet through console server
                    # may not show "login:" invitation instantly.only after endline reception
                    # so "endline" will be send
                    #self.session.send('\n')
                    self.session.sendline('')
                    logging.debug('endline sent')
                    # user may be already authenticated so device hostname or --More-- line are expected
                    first_output = self.session.expect(['#', '--More--', 'login:'])
                    logging.debug('# More & login expectation:' + str(first_output))
                    if first_output != 2:
                        logging.info('Already authenticated')
                        if first_output == 1:
                            logging.info('--More-- invitation found')
                            self.session.sendline('q')
                        logging.info(f'Already connected to console server '
                                     f'{str(self.ip)} via telnet port {str(self.port)}')
                        self.start_session_log(self.session,
                                               self.connection_name,
                                               self.test_name)
                        return True
                    else:
                        self.session.sendline(self.username)
                        self.session.expect('Password:')
                        self.session.sendline(self.password)
                        self.session.expect(self.terminal_basic_prompt)
                        self.session.sendline(self.terminal_exec_command)
                        self.session.expect(self.terminal_exec_prompt)
                        logging.info(f'Successfully connected to console server '
                                     f'{str(self.ip)} via telnet port {str(self.port)}')
                        self.start_session_log(self.session,
                                               self.connection_name,
                                               self.test_name)
                        return True
                # common telnet connection
                logging.debug('Applying credentials')
                if self.protocol == 'telnet':
                    self.session.expect('login:')
                self.session.sendline(self.username)
                logging.debug('login pass')
                self.session.expect('Password:')
                logging.debug('password pass')
                self.session.sendline(self.password)
                self.session.expect(self.terminal_basic_prompt)
                #logging.debug(self.terminal_basic_prompt + ' pass')
                self.session.sendline(self.terminal_exec_command)
                #logging.debug(self.terminal_exec_command + ' sent')
                self.session.expect(self.terminal_exec_prompt)
                #logging.debug(self.terminal_exec_prompt + ' pass')
                # closing log to file
                # self.child.logfile = None
                # fout.close()
                logging.info(f'Successfully connected to {str(self.ip)} via telnet port {str(self.port)}')
                self.start_session_log(self.session,
                                       self.connection_name,
                                       self.test_name)
                return True

            except pexpect.TIMEOUT:
                logging.info('Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before)
                return result
            except pexpect.EOF:
                logging.info(('Connection to the device {} received unexpected output').format(str(self.ip)))
                logging.debug(self.session.before)
                return result

        elif self.protocol == 'ssh':
            try:
                credentials = 'ssh ' + self.username + '@' + str(self.ip)
                # If ssh keys is not found, they will be added automatically
                self.session = pexpect.spawn(credentials, timeout=30)
                time.sleep(5)
                self.session.expect('password:')
                self.session.sendline(self.password)
                self.session.sendline('enable')
                logging.debug(f'Successfully connected to {str(self.ip)} via ssh port {str(self.port)}')
                self.start_session_log(self.session,
                                       self.connection_name,
                                       self.test_name)
                return True
            except pexpect.TIMEOUT:
                logging.info(
                    'Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return result
            except pexpect.EOF:
                logging.info((
                    'Connection to the device {} received unexpected output')
                    .format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return result

    def start_session_log(self,
                          session_instance,
                          connection_name,
                          test_name):
        log_filename = connections_log_path + test_name + "/" + connection_name + ".log"
        fout = open(log_filename, "wb+")
        session_instance.logfile = fout
        logging.info('Log session ' + connection_name + ' to file ' + log_filename)

    def logout(self):
        if self.session.isalive():
            self.session.sendline('exit')
            time.sleep(5)
            #==part for aruba switches==
            self.session.sendline('exit')
            time.sleep(5)
            self.session.sendline('exit')
            time.sleep(5)
            self.session.sendline('y')
            #===========================
            self.session.close()
            return True
        self.session.kill(signal.SIGKILL)
        return True

    def login_aruba(self):
        result = False
        if self.protocol == 'telnet' or self.protocol == 'console':
            try:
                credentials = 'telnet ' + str(self.ip) + ' ' + str(self.port)
                self.session = pexpect.spawn(credentials, timeout=30)
                # telnet connection over console server
                if self.protocol == 'console':
                    # if remote device refuses connection session process terminates immediately
                    # check session process existence
                    if psutil.pid_exists(self.session.pid) == False:
                        logging.info('Device {host} connection refused.'.format(host=str(self.ip)))
                        return False
                    # connection to device console port via telnet through console server
                    # "double enter" invintation
                    self.session.sendline('\r\n')
                    time.sleep(5)
                    self.session.sendline('\r\n')
                    time.sleep(15)
                    # "press any key to continue" invintation
                    self.session.sendline('\r\n')
                    time.sleep(15)
                    self.session.sendline('enable')
                    self.session.expect('#')
                    logging.info(f'Already connected to console server '
                                 f'{str(self.ip)} via telnet port {str(self.port)}')
                    self.start_session_log(self.session,
                                           self.connection_name,
                                           self.test_name)
                    return True
            except pexpect.TIMEOUT:
                logging.info('Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before)
                return result
            except pexpect.EOF:
                logging.info(('Connection to the device {} received unexpected output').format(str(self.ip)))
                logging.debug(self.session.before)
                return result

        elif self.protocol == 'ssh':
            try:
                credentials = 'ssh ' + self.username + '@' + str(self.ip)
                # If ssh keys is not found, they will be added automatically
                self.session = pexpect.spawn(credentials, timeout=30)
                time.sleep(5)
                self.session.expect('password:')
                self.session.sendline(self.password)
                self.session.sendline('enable')
                logging.debug(f'Successfully connected to {str(self.ip)} via ssh port {str(self.port)}')
                self.start_session_log(self.session,
                                       self.connection_name,
                                       self.test_name)
                return True
            except pexpect.TIMEOUT:
                logging.info(
                    'Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return result
            except pexpect.EOF:
                logging.info((
                    'Connection to the device {} received unexpected output')
                    .format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return result
    '''
    def logout_aruba(self):
        if self.session.isalive():
            self.session.sendline('reload')
            time.sleep(5)
            self.session.sendline('y')
            self.session.close()
            return True
        self.session.kill(signal.SIGKILL)
        return True
    '''

