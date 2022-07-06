import uuid
'''
Class represents network node under test
'''
class Node():

    ''''
    Class expects arguments:
    -nodetype{7510-48qx,7510-32c,7700-48q...}
    -hostname{tr1}
    '''
    def __init__(self, hostname, type):
        id = str(uuid.uuid4()).split('-')[0]
        self.id = 'nod' + id[0] + id[1]
        self.type = type
        self.hostname = hostname

    def get_type(self):
        return self.type

    def get_name(self):
        return self.hostname

    def get_id(self):
        return self.id





