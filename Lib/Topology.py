from Lib.Node import Node
from Lib.Link import Link

class Topology():
    '''
    Class represents basic operations with nodes and links in topology
    -Add new node(ixia node)
    -Remove node(ixia node)
    -Edit node(ixia node)
    -Show node(ixia node)
    -List topology nodes(ixia nodes)
    -Add new link
    -Remove link
    -Check link
    '''

    def __init__(self, name):
        self.name = name
        self.nodelist = []
        self.linklist = []

    def get_name(self):
        return self.name

    def get_nodelist(self):
        return self.nodelist

    def add_node(self, hostname, type):
        for node in self.nodelist:
            if node.type == type and node.hostname == hostname:
                #node already exist
                return 0
        self.nodelist.append(Node(hostname, type))

    def remove_node(self, id):
        node_check = False
        for node in self.nodelist:
            if len(self.nodelist) > 0:
                if node.id == id:
                    node_check = True
                    self.nodelist.remove(node)
                    break
            else:
                #node not found
                return 0
        if node_check == False:
            #node not found
            return 0

    def add_link(self,hostnameA,portA,hostnameB,portB):
        self.linklist.append(Link(hostnameA,portA,hostnameB,portB))

    def remove_link(self, id):
        link_check = False
        for link in self.linklist:
            if len(self.linklist) > 0:
                if link.id == id:
                    link_check = True
                    self.linklist.remove(link)
                    break
            else:
                 # link not found
                 return 0
        if link_check == False:
            # link not found
            return 0






