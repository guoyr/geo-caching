from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from coordinator_commands import *
class CoordinatorProtocol(AMP):

    @FecthData.responder
    def fetchData(self, msg):
        #TODO: msg contains the 
        