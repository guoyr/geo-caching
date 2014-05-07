from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from coordinator_commands import *

class CoordinatorProtocol(AMP):

    @FetchData.responder
    def fetchData(self, msg):
        #TODO: msg contains the 
        pass

    @GetMaster.responder
    def getMaster(self, USER_UID_KEY):
    	#TODO
    	master_id = "WEST"
    	return {MASTER_SERVER_ID, master_id}

class CoordinatorFactory(Factory):
    protocol=CoordinatorProtocol