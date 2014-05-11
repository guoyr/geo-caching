#handles image transfers

import sys
sys.path.insert(0, "../")
import json
import datetime

from pymongo import MongoClient
from pymongo import errors
import gridfs

from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.python.log import err
from twisted.protocols.basic import FileSender
from twisted.web.resource import NoResource

from coordinator_commands import *
from store_commands import *
from factory_manager import FactoryManager
from settings import *
from constants import *
from twisted.web.client import Agent, readBody

CACHE_SIZE = 5

class ImageTransferResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "image/jpeg")
        if (len(request.args) < 2): return NoResource()
        image_name = request.args[IMAGE_UID_KEY][0]
        user = request.args[USER_UID_KEY][0]
        is_client = int(request.args[IS_CLIENT_KEY][0])
        latency = float(request.args[LATENCY_KEY][0])
        image = get_image(image_name, user)
        #TODO: add latency

        if is_client:
            d = FactoryManager().get_coordinator_client_deferred()

            #add access record first
            def add_access_record(protocol):
                return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, is_save=False, latency_key=latency, to_key="CLIENT", from_key=SERVER_ID)
            

            def err_add_access_record_handler(failure):
                print "###########################"
                print "unable to add access record"
                print "###########################"
                raise errors.ConnectionFailure

            d.addErrback(err_add_access_record_handler)
            d.addCallback(add_access_record)

            if image:
                #cache has image
                #TODO: update image access time
                print "cache has the image, now sending..."
                send_open_file(image, request)
            else:
                d = FactoryManager().get_coordinator_client_deferred()
                #image doesn't exist on cache, try get it on master
                print("image does not exist, trying to get from master...")
                def check_coordinator(protocol):

                    #add_image_rec
                    d = FactoryManager().get_coordinator_client_deferred()
            
                    def c(protocol):
                        return protocol.callRemote(GetMaster, user_uid_key=user)
                    #d.addErrback(err_get_master)
                    d.addCallback(c)

                    def parse_master_id(response):
                        print("cache parse master id")
                        master_id = response[MASTER_SERVER_ID]
                        print("master: " + str(master_id))
                        fetch_image(master_id, image_name, user, False, request)

                    d.addCallback(parse_master_id)

                d.addCallback(check_coordinator)

        else:
            #cache request image from master
            if image:
                print "sending image to non-client..."

                send_open_file(image, request)
            else:
                print "Error: master should always have image"
                request.write(json.dumps(["Error: master doesn't have image"]))
                request.finish()

        return NOT_DONE_YET            

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")

        image_name = request.args[IMAGE_UID_KEY][0]
        image = request.args[image_name][0]
        user = request.args[USER_UID_KEY][0]
        latency = float(request.args[LATENCY_KEY][0])

        # assume image is unique, check is on client
        # check if master
        print("image name" + image_name)
        print("user" + user)
        d = FactoryManager().get_coordinator_client_deferred()
        print("get deferred")

        #add the record first
        def add_access_record(protocol):
            print("add access record")
            print(protocol)
            return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, is_save=True, latency_key=latency, to_key=SERVER_ID, from_key="CLIENT")
        d.addCallback(add_access_record)

        def check_coordinator(response):
            #add_image_rec
            print("check coordinator")
            print(type(response))
            d = FactoryManager().get_coordinator_client_deferred()
            
            def c(protocol):
                return protocol.callRemote(GetMaster, user_uid_key=user)
            d.addCallback(c)

            def parse_master_id(response):
                print("parse master_id")
                master_id = response[MASTER_SERVER_ID]
                if master_id == SERVER_ID:
                    print "is master"
                    save_image_master(image, image_name, user)
                else:
                    print "is not master"
                    save_image_LRU_cache(image, image_name, user)
                    print "saved image on local cache"
                    request_master_image_download(master_id, image_name, user)
                    print "finish requesting"

                request.write(json.dumps(["upload complete"]))
                request.finish()

            d.addCallback(parse_master_id)

        d.addCallback(check_coordinator)

        # call done at end of save_image
        return NOT_DONE_YET

# IMAGE METHODS



def get_image(name,user):
# get the gridout object of stored file by _id.
    fs = connect_image_fs()
    info_db = connect_image_info_db()

    image_info = info_db[user].find_one({"name":name})
    
    #image doesn't exist
    if not image_info:
        return None
    uid = image_info["gridfs_uid"]
    f = fs.get(uid)

    #update the views and the last_used_time
    time = datetime.datetime.now()
    image_info["views"] = image_info["views"] + 1
    image_info["last_used_time"] = time
    info_db[user].save(image_info)
    print ("picture: " + str(uid) + " viewed " + str(image_info['views']) + " times. Last used time: " + str(image_info['last_used_time']))
    return f


# HELPER METHODS

def save_image_master(image, name, user):
    # I am the master, save the image to master collection without the cache size limitation
    db = connect_image_info_db()
    fs = connect_image_fs()

    uid = fs.put(image)
    time = datetime.datetime.now()
    image_info = {
        "name":name,
        "gridfs_uid":uid,
        "user_uid":user,
        "last_used_time":time,
        "creation_time":time,
        "views":0
    }
    db[user].save(image_info)
    print ("image stored in master: " +  SERVER_ID)

def save_image_LRU_cache(image, image_name, user):
    db = connect_image_info_db()
    fs = connect_image_fs()
    print "db and fs were constructed"
    if db[user].count() >= CACHE_SIZE:
        print "cache is full, remove the least used one"
        image_info_cursor = db[user].find().sort("last_used_time",1).limit(1)
        for image_info in image_info_cursor:
            fs.delete(image_info["gridfs_uid"])
            db[user].remove(image_info["_id"])

    print "putting image..."
    uid = fs.put(image)
    time = datetime.datetime.now()
    image_info = {
        "name":image_name,
        "gridfs_uid":uid,
        "user_uid": user,
        "last_used_time": time,
        "creation_time": time,
        "views": 0
    }
    print "saving image info..."
    db[user].save(image_info)

def send_open_file(openFile, request):
    '''Use FileSender to asynchronously send an open file

    [JBY] From: http://stackoverflow.com/questions/1538617/http-download-very-big-file'''
    print("starting trasnferring file...")
    dd = FileSender().beginFileTransfer(openFile, request)

    def cbFinished(ignored):
        openFile.close()
        request.finish()
    
    dd.addErrback(err)
    dd.addCallback(cbFinished)

def fetch_image(store_name, image_name, user, isMaster, request=None):
    print("cache trying to fetch image from master")

    d = FactoryManager().get_coordinator_client_deferred()

    # cache fetch to master
    def add_access_record(protocol):
        return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, is_save=False, latency_key=SERVER_LATENCY, from_key="other", to_key=SERVER_ID)
    
    def err_add_access_record_handler(failure):
        print "###########################"
        print "unable to add access record"
        print "###########################"
        raise errors.ConnectionFailure

    d.addErrback(err_add_access_record_handler)
    d.addCallback(add_access_record)

    from twisted.internet import reactor    
    agent = Agent(reactor)
    print("agent created")
    uri = "http://"+store_name+"-5412.cloudapp.net:"+str(HTTP_PORT)+"/image/"
    args = "?%s=%s&%s=%s&%s=%d&%s=%f" %(IMAGE_UID_KEY, image_name, USER_UID_KEY, user, IS_CLIENT_KEY, 0, LATENCY_KEY, SERVER_LATENCY)
    d = agent.request('GET', uri+args, None, None)
    print("request made")
    def image_received(response):
        print "cache trying to receive image"
        d = readBody(response)
        print "cache received image"
        d.addCallback(cbBody)

    def cbBody(image):
        if isMaster:
            #image retrieved from cache
            save_image_master(image, image_name, user)
        else:
            #image requested by client and retrieved from master
            #save image
            #send image
            save_image_LRU_cache(image, image_name, user)
            serving_image = get_image(image_name, user)
            send_open_file(serving_image, request)

    d.addCallback(image_received)

def request_master_image_download(master_id, name, user):
    d = FactoryManager().get_store_client_deferred()

    def push_image(protocol):
        print "start requesting master for downloading picture"
        return protocol.callRemote(SendSingleImageInfo, cache_uid_key=SERVER_ID, user_uid_key=user, image_uid_key=name)

    d.addCallback(push_image)

def connect_image_fs():
    db = MongoClient().image_db
    fs = gridfs.GridFS(db)
    return fs

def connect_image_info_db():
    db = MongoClient().image_info_db
    return db

def get_image_factory():
    resource = Resource()
    resource.putChild('image', ImageTransferResource())
    factory = Site(resource)
    return factory


