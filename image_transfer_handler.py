#handles image transfers

import sys
import json

from pymongo import MongoClient
import gridfs

from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.python.log import err
from twisted.protocols.basic import FileSender
from twisted.web.resource import NoResource

IMAGE_UID_KEY = "image_uid_key"
DEVICE_UID_KEY = "device_uid_key"


class ImageTransferResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "image/jpeg")
        clean_path = request.path.strip("/")
        paths = clean_path.split("/")
        if (len(paths) < 2): return NoResource()

        image_name = paths[1]
        image = get_image(image_name)
        if image:
            self.sendOpenFile(request, image)
        else:
            return NoResource()

        return NOT_DONE_YET

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")

        image_name = request.args[IMAGE_UID_KEY][0]
        image = request.args[image_name][0]
        device = request.args[DEVICE_UID_KEY][0]

        save_image(image, image_name, device)
        return json.dumps(["client image post1"])


    def sendOpenFile(self, request, openFile):
        '''Use FileSender to asynchronously send an open file

        [JBY] From: http://stackoverflow.com/questions/1538617/http-download-very-big-file'''

        dd = FileSender().beginFileTransfer(openFile, request)

        def cbFinished(ignored):
            openFile.close()
            request.finish()
        
        dd.addErrback(err)
        dd.addCallback(cbFinished)
        return NOT_DONE_YET

def save_image(image, name, device):
# save the pic specified by the full_path + file_name, return the _id in gridfs
    fs = connect_image_db()
    uid = fs.put(image)

    info_db = connect_image_info_db()
    image_info = {
        "name":name,
        "gridfs_uid":uid,
        "device_uid": device
    }
    info_db.insert(image_info)
    return 

def get_image(name):
# get the gridout object of stored file by _id.
    fs = connect_image_db()
    info_db = connect_image_info_db()

    image_info = info_db.find_one({"name":name})
    uid = image_info["gridfs_uid"]
    f = fs.get(uid)
    return f

def connect_image_db():
    db = MongoClient().image_db
    fs = gridfs.GridFS(db)
    return fs

def connect_image_info_db():
    db = MongoClient().image_info_db
    return db.info

def get_image_factory():
    resource = Resource()
    resource.putChild('image', ImageTransferResource())
    factory = Site(resource)
    return factory