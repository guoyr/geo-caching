from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory

from constants import *
from coordinator_commands import *
from store_commands import *
from utils import *

class CoordinatorProtocol(AMP):

    @GetMaster.responder
    def getMaster(self, user_uid_key, preferred_store):
        print_header("received request for getMaster")
        record_db = connect_user_record_db()
        user_record = record_db["records"].find_one({"uid":user_uid_key})
        if user_record:
            master_id = str(user_record["master"])
        else:
        	master_id = str(preferred_store)
        
        closeConnection(self.transport)

    	return {MASTER_SERVER_ID: master_id}

    @AddAccessRecord.responder
    def addRecord(self, image_uid_key, user_uid_key, preferred_store, latency_key, from_key, to_key):
        # piggyback latency information here, use from, to to determine where called by server
        print_header("received request for add record")
        if to_key == "CLIENT" or from_key=="CLIENT":
            print_header("received request for addRecord")
            record_db = connect_user_record_db()
            user_record = record_db["records"].find_one({"uid":user_uid_key})
            if not user_record:
                user_record = {
                    "uid":user_uid_key,
                    "preferred_store":preferred_store,
                    "master":preferred_store,
                    "preferred_store_access_count":1,
                    "master_access_count":1
                }
                record_db["records"].save(user_record)
            else:
                if(preferred_store == user_record["master"]):
                    user_record["master_access_count"] += 1
                    if(user_record["preferred_store"] != preferred_store):
                        user_record["preferred_store"] = preferred_store
                        user_record["preferred_store_access_count"] = 1
                    else:
                        user_record["preferred_store_access_count"] += 1
                else:
                    #if there are more than 1 cache
                    if(user_record["preferred_store"] != preferred_store):
                        user_record["preferred_store"] = preferred_store
                        user_record["preferred_store_access_count"] = 1
                    else:
                        user_record["preferred_store_access_count"] += 1

                    #change master should happen if this condition met
                    if(user_record["preferred_store_access_count"] > user_record["master_access_count"]):
                        #change the master loc
                        self.changeMaster(preferred_store, user_record["master"], user_uid_key)

                        user_record["master"] =  preferred_store
                        user_record["master_access_count"] = 1
                        user_record["preferred_store"] = preferred_store
                        user_record["preferred_store_access_count"] = 1

                record_db["records"].save(user_record)
        
        # parse latency information
        if to_key != "CLIENT" and from_key != "CLIENT":
            if to_key == "EAST": 
                from_key = "WEST" 
            else: 
                from_key = "EAST"
        LatencyCache[user_uid_key].append([from_key, to_key, latency_key])

        closeConnection(self.transport)
        return {"success": True}

    
    def changeMaster(self, new_master, old_master, user):
        print_header("initiating change master")
        from factory_manager import FactoryManager
        #get two deferred for each server
        d = FactoryManager().get_store_client_deferred(serverIDToServer(new_master))

        def notify_new_master(protocol):
            return protocol.callRemote(InitiateMasterChange, user_uid_key=str(user), old_master_key=str(old_master))

        d.addCallback(notify_new_master)
        #TODO: add errback, if cache not available, revert master change

class CoordinatorFactory(Factory):
    protocol=CoordinatorProtocol