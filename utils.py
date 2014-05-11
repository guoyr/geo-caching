import datetime
import json

from pymongo import MongoClient
import gridfs

from constants import *

def print_header(msg):
    print bcolors.HEADER + msg + bcolors.ENDC

def print_okblue(msg):
    print bcolors.OKBLUE + msg + bcolors.ENDC

def print_okgreen(msg):
    print bcolors.OKGREEN + msg + bcolors.ENDC

def print_warning(msg):
    print bcolors.WARNING + msg + bcolors.ENDC

def print_fail(msg):
    print bcolors.FAIL + msg + bcolors.ENDC

def print_log(msg):
    print bcolors.LOG + msg + bcolors.ENDC

def closeConnection(conn):
    from twisted.internet import reactor
    def c():
        conn.loseConnection()
    reactor.callLater(TIMEOUT, c)

def serverIDToServer(serverID):
	if serverID == "WEST":
		return "west-5412.cloudapp.net"
	elif serverID == "EAST":
		return "east-5412.cloudapp.net"
	else:
		return "clientdb-5412.cloudapp.net"

def connect_image_fs():
    db = MongoClient().image_db
    fs = gridfs.GridFS(db)
    return fs

def connect_image_info_db():
    db = MongoClient().image_info_db
    return db

def connect_user_record_db():
    db = MongoClient().record_db
    return db

def save_image_master(image, name, user, callback=None):
    print_log("saving image to master")
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
    if callback:
        callback()

def save_image_LRU_cache(image, image_name, user):
    db = connect_image_info_db()
    fs = connect_image_fs()
    if db[user].count() >= CACHE_SIZE:
        print_okgreen("cache is full, remove the least used one")
        image_info_cursor = db[user].find().sort("last_used_time",1).limit(1)
        for image_info in image_info_cursor:
            fs.delete(image_info["gridfs_uid"])
            db[user].remove(image_info["_id"])

    print_log("putting image in cache")
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
    db[user].save(image_info)

def request_write_error_finish(request, err):
    request.write(json.dumps({"Error":err}))
    request.finish()
