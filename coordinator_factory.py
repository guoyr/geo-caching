from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from coordinator_commands import *
from pymongo import MongoClient

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
    	return {MASTER_SERVER_ID: master_id}

    @AddAccessRecord.responder
    def addRecord(self, user_id, preferred_store, is_save):
        print("received request for addRecord")
        print("is_save:" + str(is_save))
        record_db = self.connect_user_record_db()
        user_record = record_db["records"].find_one({"uid":user_id})
        if not user_record:
            user_record = {
                "uid":user_id,
                "preferred_store":preferred_store,
                "is_save":is_save
            }
            record_db["records"].save(user_record)
        else:
            user_record["preferred_store"] = preferred_store
            user_record["is_save"] = is_save
            record_db["records"].save(user_record)
        return {"success": True}

    def connect_user_record_db(self):
        db = MongoClient().record_db
        return db
        
class CoordinatorFactory(Factory):
    protocol=CoordinatorProtocol