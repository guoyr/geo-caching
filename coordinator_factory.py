from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from coordinator_commands import *

class CoordinatorProtocol(AMP):

    @FetchData.responder
    def fetchData(self, msg):
        #TODO: msg contains the 
        pass

    @GetMaster.responder
    def getMaster(self, user_id):
    	#TODO
        print "received request for getMaster"
    	master_id = "WEST"
    	return {MASTER_SERVER_ID, master_id}

    @AddAccessRecord.responder
    def addRecord(self, user_id, preferred_store, is_save):
        print("received request for addRecord")
        return {"success": True}

class CoordinatorFactory(Factory):
    protocol=CoordinatorProtocol