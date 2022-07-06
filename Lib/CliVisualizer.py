from Lib.SystemConstants import CLI_ARROW, CLI_SLASH
import logging

class CliVisualizer():
    '''
    Represent several view modes for console interface and print data accoding this view modes

    Cli view modes:
    -Global
    -Topology
    -Node
    -Link
    -NodeAutotest
    -LinkAutotest
    '''

    def __init__(self):
        self.cli_view_mode = {'mode':'GLOBAL',
                              'topology':'none',
                              'node':'none',
                              'link':'none',
                              'step':'0'}
        logging.basicConfig(level=logging.INFO)
        #logging.info('Logging start')


    def set_cli_view_parametres(self, mode, topology=None, node=None, link=None, step=None):
        self.cli_view_mode['mode'] = mode
        self.cli_view_mode['topology'] = topology
        self.cli_view_mode['node'] = node
        self.cli_view_mode['link'] = link


    def get_cli_view_mode(self):
        mode_name = self.cli_view_mode['mode']
        topology_name = self.cli_view_mode['topology']
        node_name = self.cli_view_mode['node']
        link_name = self.cli_view_mode['link']

        if mode_name == 'GLOBAL':
            result = CLI_ARROW
        if mode_name == 'TOPOLOGY':
            result = topology_name + CLI_ARROW
        if mode_name == 'NODE':
            result = topology_name + CLI_SLASH + node_name + CLI_ARROW
        if mode_name == 'LINK':
            result = topology_name + CLI_SLASH + link_name + CLI_ARROW
        return result

    '''
    displays message in cli.
    text - text to display
    output_flag - set message output method
    "print" - output via print() function
    "logging_info - via logging.info()
    "logging_debug - via logging.debug()
    '''


    def message(self, text, output_flags):

        if "print" in output_flags:
            print(text)
        if "logging_info" in output_flags:
            logging.info(text)
        if "logging_debug" in output_flags:
            logging.debug(text)

        '''
        Print data accroding to cli view mode
        />			                	     cli_view_mode = {'mode':'GLOBAL'}
        /topology_name>			             cli_view_mode = {'mode':'TOPOLOGY',
                                                              'topology':'topology_name'}
        /topology_name/node_name>			 cli_view_mode = {'mode':'NODE',
                                                              'topology':'topology_name',
                                                              'node':'node_name')
        /topology_name/link_name>		     cli_view_mode = {'mode':'LINK',
                                                              'topology':'topology_name',
                                                              'node':'node_name',
                                                              'link':'link_name'}
        /topology_name/node_name(stepN)>     cli_view_mode = {'mode':'NODE&AUTOTEST',
                                                              'topology':'topology_name',
                                                              'node':'node_name',
                                                              'step':'N')
        /topology_name/ink_name(stepN)>      cli_view_mode = {'mode':'LINK&AUTOTEST',
                                                              'topology':'topology_name',
                                                              'node':'node_name',
                                                              'link':'link_name',
                                                              'step':'N')
        '''

        '''
        mode_name = self.cli_view_mode['mode']
        topology_name = self.cli_view_mode['topology']
        node_name = self.cli_view_mode['node']
        link_name = self.cli_view_mode['link']
        #step = self.cli_view_mode['step']

        #if flag false print text on the present line
        if  newline_flag == False:
            #sys.stdout.write(CLI_SLASH + CLI_ARROW) D
            sys.stdout.write(text)
            #print(text)
            #pass
        #else print text end go to next line
        else:

            if  mode_name == 'GLOBAL':
                #pass
                #sys.stdout.write(CLI_SLASH + CLI_ARROW + text)
                #print(text)
                sys.stdout.write(text)
                #print(CLI_SLASH + CLI_ARROW + text) D
                #sys.stdout.write(CLI_SLASH + CLI_ARROW) D
            if  mode_name == 'TOPOLOGY':
                print(topology_name + CLI_ARROW + text)
                sys.stdout.write(topology_name + CLI_ARROW)
            if  mode_name == 'NODE':
                print(CLI_SLASH + topology_name + CLI_SLASH + node_name + CLI_ARROW + text)
                sys.stdout.write(CLI_SLASH + topology_name + CLI_SLASH + node_name + CLI_ARROW)
            if  mode_name == 'LINK':
                print(CLI_SLASH + topology_name + CLI_SLASH + link_name + CLI_ARROW + text)
                sys.stdout.write(CLI_SLASH + topology_name + CLI_SLASH + link_name + CLI_ARROW)
        '''








