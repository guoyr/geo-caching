#handles image transfers

import sys
sys.path.insert(0, "../")
import json


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
from utils import *
from twisted.web.client import Agent, readBody

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

        if is_client:
            print_log("GET request from client")

            d = FactoryManager().get_coordinator_client_deferred()

            #add access record first
            def add_access_record(protocol):
                return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, latency_key=latency, to_key="CLIENT", from_key=SERVER_ID)
            

            def err_add_access_record_handler(failure):
                print_fail("unable to add access record")
                # request_write_error_finish(request, "unable to add access record")
                return
                

            d.addCallback(add_access_record).addErrback(err_add_access_record_handler)

            if image:
                #cache has image
                print_log("store has image, now sending to client")
                send_open_file(image, request)
            else:
                d = FactoryManager().get_coordinator_client_deferred()
                #image doesn't exist on cache, try get it on master
                print_log("cache doesn't have image, querying coordinator for master")
                def check_coordinator(protocol):

                    #add_image_rec
                    d = FactoryManager().get_coordinator_client_deferred()
            
                    def c(protocol):
                        return protocol.callRemote(GetMaster, user_uid_key=user, preferred_store=SERVER_ID)
                    
                    def err_get_master_handler(failure):
                        print_fail("unable to get master")
                        request_write_error_finish(request, "Internal error, please try again later")

                    d.addCallback(c).addErrback(err_get_master_handler)

                    def parse_master_id(response):
                        master_id = response[MASTER_SERVER_ID]
                        print_log("got master: " + str(master_id))
                        fetch_image(master_id, image_name, user, False, request)

                    d.addCallback(parse_master_id)

                d.addCallback(check_coordinator)


        else:
            if image:
                print_log("sending image to cache or master")
                send_open_file(image, request)
            else:
                print_fail("Error: master should always have image")
                request_write_error_finish(request, "master doesn't have image")

        return NOT_DONE_YET            


    def render_POST(self, request):
        print_log("POST request from client")
        request.setHeader("content-type", "application/json")
        image_name = request.args[IMAGE_UID_KEY][0]
        image = request.args[image_name][0]
        user = request.args[USER_UID_KEY][0]
        latency = float(request.args[LATENCY_KEY][0])

        #add_image_rec
        d = FactoryManager().get_coordinator_client_deferred()
        
        def get_master(protocol):
            return protocol.callRemote(GetMaster, user_uid_key=user, preferred_store=SERVER_ID)

        def err_post_master_handler(failure):
            print_fail("Can't get master")
            request_write_error_finish(request, "can't get master")

        d.addCallback(get_master).addErrback(err_post_master_handler)

        def parse_master_id(response):
            master_id = response[MASTER_SERVER_ID]
            if master_id == SERVER_ID:
                print_log("I am master, saving image to disk")
                save_image_master(image, image_name, user)
            else:
                print_log("I am not master, saving image to cache and request master to get it")
                save_image_LRU_cache(image, image_name, user)
                request_master_image_download(master_id, image_name, user)

            d = FactoryManager().get_coordinator_client_deferred()

            #add the record last because we need to save image to master first
            def add_access_record(protocol):
                return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, latency_key=latency, to_key=SERVER_ID, from_key="CLIENT")

            def err_add_access_record_handler(failure):
                print_fail("unable to add access record")
                # request_write_error_finish(request, "unable to add access record")
                return

            d.addCallback(add_access_record).addErrback(err_add_access_record_handler)

            request.write(json.dumps(["upload complete"]))
            request.finish()

        def err_get_master_handler(failure):
            print_fail("unable to get master")
            request_write_error_finish(request, "Internal error, please try again later")

        d.addCallback(parse_master_id).addErrback(err_get_master_handler)

        return NOT_DONE_YET

# IMAGE METHODS
def get_image(name,user):
# get the gridout object of stored file by _id.
    fs = connect_image_fs()
    info_db = connect_image_info_db()
    image_info = info_db[user].find_one({"name":name})
    
    #image doesn't exist
    if not image_info: return None
    uid = image_info["gridfs_uid"]
    f = fs.get(uid)

    #update the views and the last_used_time
    time = datetime.datetime.now()
    image_info["views"] = image_info["views"] + 1
    image_info["last_used_time"] = time
    info_db[user].save(image_info)
    # print ("picture: " + str(uid) + " viewed " + str(image_info['views']) + " times. Last used time: " + str(image_info['last_used_time']))
    return f


# HELPER METHODS
def send_open_file(openFile, request):
    '''Use FileSender to asynchronously send an open file

    [JBY] From: http://stackoverflow.com/questions/1538617/http-download-very-big-file'''
    dd = FileSender().beginFileTransfer(openFile, request)

    def cbFinished(ignored):
        openFile.close()
        request.finish()
    
    dd.addCallback(cbFinished).addErrback(err)

def fetch_image(store_name, image_name, user, isMaster, request=None, callback=None):
    #cache trying to fetch image from master
    print_log("cache trying to fetch image from master")

    d = FactoryManager().get_coordinator_client_deferred()

    # cache fetch to master
    def add_access_record(protocol):
        return protocol.callRemote(AddAccessRecord, image_uid_key=image_name,user_uid_key=user, preferred_store=SERVER_ID, latency_key=SERVER_LATENCY, from_key="other", to_key=SERVER_ID)

    def err_add_access_record_handler(failure):
        print_fail("unable to add access record")
        # request_write_error_finish(request, "unable to add access record")
        return

    d.addCallback(add_access_record).addErrback(err_add_access_record_handler)

    from twisted.internet import reactor    
    agent = Agent(reactor)
    uri = "http://"+store_name.lower()+"-5412.cloudapp.net:"+str(HTTP_PORT)+"/image/"
    args = "?%s=%s&%s=%s&%s=%d&%s=%f" %(IMAGE_UID_KEY, image_name, USER_UID_KEY, user, IS_CLIENT_KEY, 0, LATENCY_KEY, SERVER_LATENCY)
    d = agent.request('GET', uri+args, None, None)
    print_log("GET: " + uri+args)
    def cbBody(image):
        if isMaster:
            #image retrieved from cache
            print_log("retrieved image from cache, saving to disk")
            save_image_master(image, image_name, user, callback)
        else:
            #image requested by client and retrieved from master
            print_log("retrieved image from master, cachinng it locally and sending it to client")
            save_image_LRU_cache(image, image_name, user)
            serving_image = get_image(image_name, user)
            send_open_file(serving_image, request)

    def err_parse_image_handler(failure):
        print_fail("unable to parse image from store")

    def image_received(response):
        d = readBody(response)
        d.addCallback(cbBody).addErrback(err_parse_image_handler)

def request_master_image_download(master_id, name, user):
    d = FactoryManager().get_store_client_deferred()

    def push_image(protocol):
        print_log("start requesting master for downloading picture")
        return protocol.callRemote(SendSingleImageInfo, cache_uid_key=SERVER_ID, user_uid_key=user, image_uid_key=name)

    d.addCallback(push_image)
    d.addErrback(err)

def get_image_factory():
    resource = Resource()
    resource.putChild('image', ImageTransferResource())
    factory = Site(resource)
    return factory


