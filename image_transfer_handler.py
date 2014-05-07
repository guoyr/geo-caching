#handles image transfers

import sys
sys.path.insert(0, "../")
import json
import datetime

from pymongo import MongoClient
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


CACHE_SIZE = 5

class ImageTransferResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "image/jpeg")
        if (len(request.args) < 2): return NoResource()
        image_name = request.args[IMAGE_UID_KEY][0]
        user = request.args[USER_UID_KEY][0]
        is_client = int(request.args[IS_CLIENT_KEY][0])
        image = get_image(image_name, user)
        if image:
            self._send_open_file(request, image)
            # if from app, add record to coordinator
            # if from cache, don't have to do anything
            if is_client:
                d = FactoryManager().get_coordinator_client_deferred()
                def add_access_record(protocol):
                    return protocol.callRemote(AddAccessRecord, USER_UID_KEY=user, PREFERRED_STORE_KEY=SERVER_ID, IS_SAVE_ACTION=False)
                d.addCallback(add_access_record)
        else:
            #image doesn't exist on cache, try get it on master

        return NOT_DONE_YET

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")

        image_name = request.args[IMAGE_UID_KEY][0]
        image = request.args[image_name][0]
        user = request.args[USER_UID_KEY][0]
        latency_dict_raw = request.args[LATENCY_DICT_KEY]
        
        # array of server keys are latency values
        latency_dict = json.load(latency_dict_raw)

        # assume iamge is unique, check is on client
        save_image(image, image_name, user, latency_dict, request)

        # call done at end of save_image
        return NOT_DONE_YET


    def save_image(self, image, name, user, latency_dict, request):
        # check if master
        d = FactoryManager().get_coordinator_client_deferred()


        def check_coordinator(protocol):
            #add_image_rec
            return protocol.callRemote(GetMaster, USER_UID_KEY=user)

        d1 = d.addCallback(check_coordinator)

        def parse_master_id(response):
            master_id = response[MASTER_SERVER_ID]

            if master_id == SERVER_ID:
                save_image_master(image, name, user)
            else:
                save_image_LRU_cache(image, name, user)
                request_master_image_download(master_id, name, user)

            request.write(json.dumps(["upload complete"]))
            request.finish()

        d1.addCallback(parse_master_id)

        def add_access_record(protocol):
            return protocol.callRemote(AddAccessRecord, USER_UID_KEY=user, PREFERRED_STORE_KEY=SERVER_ID, IS_SAVE_ACTION=True)

        d.addCallback(add_access_record)

        return NOT_DONE_YET

    def _send_open_file(self, request, openFile):
        '''Use FileSender to asynchronously send an open file

        [JBY] From: http://stackoverflow.com/questions/1538617/http-download-very-big-file'''

        dd = FileSender().beginFileTransfer(openFile, request)

        def cbFinished(ignored):
            openFile.close()
            request.finish()
        
        dd.addErrback(err)
        dd.addCallback(cbFinished)
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
    db[user].insert(image_info)

def save_image_LRU_cache(image, image_name, user):
    db = connect_image_info_db()
    fs = connect_image_fs()

    if db[user].count() >= CACHE_SIZE:
        image_info = db[user].find.sort([["last_used_time",-1]]).limit(1)
        fs.delete(image_info["gridfs_uid"])
        db[user].delete(image_info["_id"])

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
    db[user].insert(image_info)

def request_master_image_download(master_id, name, user):
    d = FactoryManager().get_store_client_deferred()

    def push_image(protocol):
        return protocol.callRemote(SendSingleImageInfo, IMAGE_UID_KEY=name, CACHE_UID_KEY=SERVER_ID, USER_UID_KEY=user)

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




