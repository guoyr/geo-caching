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
    def addRecord(self, user_id, preferred_store, is_save, latency_west, latency_east):
        # if no user ID, is called by server to send latency
        print("received request for addRecord")
        print("is_save:" + str(is_save))
        record_db = self.connect_user_record_db()
        user_record = record_db["records"].find_one({"uid":user_id})
        if not user_record:
            user_record = {
                "uid":user_id,
                "preferred_store":preferred_store,
                "master":preferred_store,
                "nearest_access":1,
                "master_access":1,
                "is_save":is_save
            }
            record_db["records"].save(user_record)
        else:
            if(preferred_store == user_record["master"]):
                if(user_record["preferred_store"] != preferred_store):
                    user_record["preferred_store"] = preferred_store
                    user_record["nearest_access"] = 1
                    user_record["master_access"] += 1
                else:
                    user_record["nearest_access"] += 1
                    user_record["master_access"] += 1
            else:
                #is this condition happening?
                if(user_record["preferred_store"] != preferred_store):
                    user_record["preferred_store"] = preferred_store
                    user_record["nearest_access"] = 1
                else:
                    user_record["nearest_access"] += 1


                #change master should happen if this condition met
                if(user_record["nearest_access"] > user_record["master_access"]):
                    #change the master loc
                    user_record["master"] =  preferred_store
                    user_record["master_access"] = 1
                    user_record["preferred_store"] = preferred_store
                    iser_record["nearest_access"] = 1
                    self.changeMaster()

                    #initiate change_master action

            user_record["is_save"] = is_save


            record_db["records"].save(user_record)
        return {"success": True}

    def connect_user_record_db(self):
        db = MongoClient().record_db
        return db
    
    def changeMaster(self, new_master, user_id):
        return

class CoordinatorFactory(Factory):
    protocol=CoordinatorProtocol