import uuid

class Link():
    '''
    Class expects arguments:
    -hostnameA
    -portA
    -hostnameB
    -portB
    '''
    def __init__(self, hostnameA,portA,hostnameB,portB):
        #creating id
        id = str(uuid.uuid4()).split('-')[0]
        self.id = 'lnk' + id[0] + id[1]
        self.hostnameA = hostnameA
        self.portA = portA
        self.hostnameB = hostnameB
        self.portB = portB

    def get_id(self):
        return str(self.id)

    def get_summary(self):
        return str(self.hostnameA) + '[' + str(self.portA) + ']<>' + str(self.hostnameB) + '[' + self.portB + ']'
