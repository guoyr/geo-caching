import datetime

from pymongo import MongoClient
import gridfs

from constants import *


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

def save_image_master(image, name, user, callback=None, *args, **kwargs):
    print("saving to master")
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
        callback(*args, **kwargs)

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

