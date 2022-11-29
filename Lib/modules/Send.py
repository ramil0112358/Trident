import pexpect
import logging
from Lib.SystemConstants import logging_type
'''
Class for send and
recieve messages to Nodes.
'''
class Send():

    def __init__(self, connect_login_sessions_dict):
        self.sessions = connect_login_sessions_dict

    def sessions_update(self, connect_login_sessions_dict):
        self.sessions = connect_login_sessions_dict

    def show_sessions(self):
        for sessionID in self.sessions.keys():
            logging.info(sessionID)

    def send_command(self, sesID, command):
        try:
            sesID.sendline(command)
            logging.info("sesID before buffer: " + sesID.before.decode('utf-8').strip())
            '''
            result = sesID.expect(['>', '#'])
            while True:
                if result == 0 or result == 1:
                    logging.debug(str(result) + ' ' + sesID.before.decode('utf-8').strip())
                    break
                else:
                    logging.debug(str(result) + ' ' + sesID.before.decode('utf-8').strip())
                    
            logging.info("sesID before buffer: " + sesID.before.decode('utf-8').strip())
            '''

            # if terminal lenght != 0 and --More-- messages will be shown

            '''
            while True:
                send_result = sesID.expect(['--More--'])
                if send_result == 0:
                    #logging.info('SEND RESULT {} '.format(str(send_result)))
                    sesID.sendline(' ')
                    #logging.info(sesID.before.decode('utf-8').strip())
                else:
                    logging.info('sessionID before: ' + sesID.before.decode('utf-8').strip())
                    break
                logging.info('sessionID before again: ' + sesID.before.decode('utf-8').strip())
            '''

            return True
        except pexpect.TIMEOUT:
            logging.info('Session {} timed out'.format(str(sesID)))
            logging.info(sesID.before.decode('utf-8').strip())
            return False
        except pexpect.EOF:
            logging.info(('Session {} received unexpected output').format(str(sesID)))
            logging.info(sesID.before.decode('utf-8').strip())
            return False

    '''
    def send_command_set(self, **kwargs) -> str:
                out: str = ''
                # Concatenate path to a playbook (essentially a Jinja2 template).
                # Ansible is not in use here,
                # only his playbook style for command notation.
                playbook_path: str = (
                    'playbooks/' + self.type + '/' + kwargs['playbook'])
                # Announce explicit default VRF usage (if needed)
                if 'vrf' in kwargs and kwargs['vrf'] == ''
                    kwargs['vrf'] = 'default'
                # Jinja2 calling. It is produced filled YAML template
                env = Environment(loader=FileSystemLoader('.'),
                                  trim_blocks=True,
                                  lstrip_blocks=True)
                template = env.get_template(playbook_path)
                data_after_template = template.render(kwargs)
                # Convert filled YAML template to the ordinary python dictionary
                data_yml_format: dict = yaml.load(data_after_template)
                commands: list = data_yml_format['commands']
                # Now each of the prepared commands is sent to the device
                for command in commands:
                    self.send_command(command)
                    logging.info(
                        'Command "{}" is sent to the device {}'.format(
                            command, self.host))
                    out = self.session.before.decode('utf-8')
                logging.debug(
                    'Output from the device {} is  \r\n{}'.format(self.host, out))
                return out
    '''