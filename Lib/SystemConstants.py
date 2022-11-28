#Constants
#all avaliable ro use characters in application
VALID_COMMAND_LINE_CARACHTERS = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,.-_.,/: "'
#cli additional char
CLI_SLASH = '/'
#cli basic invintation char
CLI_ARROW = '>'
#cli maximum command length in words
MAX_COMMAND_LENGTH_IN_WORDS = 10
#maximum topologies
MAX_TOPS = 10
#maximum topology nodes
MAX_TOP_NODES = 10
#maximum_topology_links
MAX_TOP_LINKS = 100

#Paths
global_command_set_path = 'cli/commandset/'
global_command_set_filename = 'global_command_set_v2.json'
#device type specific attributes file path
devices_attr_conf_file_path = '/home/ramil/PycharmProjects/trident/Lib/device_properties/'
user_projects_folder = ''
tftp_server_ip = ''
ftp_server_ip = ''

#Logging
#logging_type = ("print", "logging_info")
logging_type = ("print")

#ixia
ixia_server_ip = "10.27.193.3"

#dut sofware update
software_server_ip = "10.121.0.147"
