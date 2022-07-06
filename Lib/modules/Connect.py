import pexpect
import logging
import time
import psutil
import uuid
import json
from Lib.SystemConstants import devices_attr_conf_file_path
import signal
import pdb
'''
Class represents connect and 
disconnect actions for Node.
'''
class Connect():

    '''
    Class attributes:
    -node instance (7510-48q6c,7510-32q,7500,7510-32c...)
    -instance id
    -protocol(telnet/ssh/console_via_telnet)
    -port to connect
    -username
    -password
    -mgmtip
    -console_server_mode
    -terminal_basic_promt
    -terminal_exec_promt
    -console_connect_expectations
    -telnet_connect_expectation
    -ssh_connect_expectation
    -terminal_exec_command
    -configuration mode command
    '''

    def __init__(self,
                 node,
                 ip,
                 protocol,
                 port,
                 username,
                 password,
                 id_counter):

        self.node = node
        self.ip = ip
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.id = 'con' + str(id_counter)

    def get_id(self):
        return self.id

    def get_nodename(self):
        return self.node.get_name()

    def get_summary(self):
        return str(self.protocol) + ' ' + \
               str(self.ip) + ':' + \
               str(self.port) + ' ' + \
               str(self.username) + '/' + \
               str(self.password)

    def login(self):
        #pdb.set_trace()
        #get node type specific attributes from json library
        device_attr_json = devices_attr_conf_file_path + str(self.node.get_type()) + '.json'
        with open(device_attr_json, "r") as read_file:
            node_attributes = json.load(read_file)
        for item in node_attributes.keys():
            setattr(self, item, node_attributes[item])

        if self.protocol == 'telnet' or self.protocol == 'contel':
            try:
                credentials = 'telnet ' + str(self.ip) + ' ' + str(self.port)
                self.session = pexpect.spawn(credentials, timeout=60)
                logging.debug('session begin')
                time.sleep(5)
                logging.debug('5 sec pass')
                # telnet connection over console server
                if self.protocol == 'contel':
                    logging.debug('contel pass')
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
                        return self.session
                    logging.debug('# More & login pass.login: line found')
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
                logging.debug(self.terminal_basic_prompt + ' pass')
                self.session.sendline(self.terminal_exec_command)
                logging.debug(self.terminal_exec_command + ' sent')
                self.session.expect(self.terminal_exec_prompt)
                logging.debug(self.terminal_exec_prompt + ' pass')
                # closing log to file
                # self.child.logfile = None
                # fout.close()
                logging.debug(f'Successfully connected to {str(self.ip)} via telnet port {str(self.port)}')
                return self.session

            except pexpect.TIMEOUT:
                logging.info('Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before)
                return False
            except pexpect.EOF:
                logging.info(('Connection to the device {} received unexpected output').format(str(self.ip)))
                logging.debug(self.session.before)
                return False

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
                return self.session
            except pexpect.TIMEOUT:
                logging.info(
                    'Connection to the device {} timed out'.format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return False
            except pexpect.EOF:
                logging.info((
                    'Connection to the device {} received unexpected output')
                    .format(str(self.ip)))
                logging.debug(self.session.before.decode('utf-8').strip())
                return False

    def logout(self, session):
        if session.isalive():
            session.sendline('exit')
            session.close()
            return True
        session.kill(signal.SIGKILL)
        return True
