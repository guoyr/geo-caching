from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from twisted.web.client import Agent, readBody

from store_commands import *
from constants import *
from utils import *

class StoreProtocol(AMP):

    @SendSingleImageInfo.responder
    def receive_image(self, user_uid_key, cache_uid_key, image_uid_key):
        from image_transfer_handler import fetch_image
        fetch_image(cache_uid_key, image_uid_key, user_uid_key, True)
        closeConnection(self.transport)
        return {"success":True}

    @InitiateMasterChange.responder
    def become_master(self, user_uid_key, old_master_key):
        # ask for list of images
        print_header("received request to become master")
        from factory_manager import FactoryManager
        d = FactoryManager().get_store_client_deferred()

        def get_image_list(protocol):
            print_header("getting list of images from old master")
            return protocol.callRemote(SendAllImages, user_uid_key=user_uid_key)
        d.addCallback(get_image_list)

        def fetch_all_images(response):
            print_header("received list of images from old master")
            from image_transfer_handler import fetch_image
            image_info_list = response["image_info_list"]
            # http://stackoverflow.com/questions/8934772/
            images_remaining = [len(image_info_list)]
            def fetched_image():
                images_remaining[0] -= 1
                if images_remaining == 0:
                    # tell old master finish transfer
                    from factory_manager import FactoryManager
                    d = FactoryManager().get_store_client_deferred()
                    def send_done(protocol):
                        print_header("fetched all images")
                        protocol.callRemote(FinishMasterTransfer, user_uid_key=user_uid_key)
                    d.addCallback(send_done)

            print_header("start fetching images: " + str(images_remaining))
            # get list of images
            for image_info in image_info_list:
                fetch_image(old_master_key, image_info, user_uid_key, True, callback=fetched_image)

        d.addCallback(fetch_all_images)
        closeConnection(self.transport)
        return {"ack":True}

    @SendAllImages.responder
    def return_list_of_image(self, user_uid_key):
        print_header("received request to get list of images")
        image_list = []
        db = connect_image_info_db()
        for image_info in db[user_uid_key].find():
            image_list.append(str(image_info["name"]))
        closeConnection(self.transport)
        return {"image_info_list": image_list}

    @FinishMasterTransfer.responder
    def ack_finish_transfer(self, user_uid_key):
        #remove all images for user in this cache
        print_header("received request to finish master transfer, removing local images")
        db = connect_image_info_db()
        fs = connect_image_fs()
        image_info_cursor = db[user_uid_key].find()
        for image_info in image_info_cursor:
            fs.delete(image_info["gridfs_uid"])
            db[user_uid_key].remove(image_info["_id"])
        closeConnection(self.transport)
        return {"success": True}

class StoreFactory(Factory):
    protocol=StoreProtocol


def main():
    from twisted.internet import reactor    
    agent = Agent(reactor)

    uri = "http://localhost:"+str(HTTP_PORT)+"/image/"

    args = "?%s=%s&%s=%s&%s=%d" %(IMAGE_UID_KEY, "1d0a0cde6aea6ad997307f01edd5c60b", USER_UID_KEY, "", IS_CLIENT_KEY, 0)

    print uri+args

    d = agent.request('GET', uri+args, None, None)

    def image_received(response):
        print vars(response)
        d = readBody(response)
        d.addCallback(cbBody)

    def cbBody(body):
        print 'Response body:'
        f = open("test_image_2.jpg","wb")
        f.write(body)
        f.close()

    d.addCallback(image_received)

    reactor.run()


if __name__ == '__main__':
    main()