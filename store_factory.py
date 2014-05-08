from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from twisted.web.client import Agent, readBody

from store_commands import *
from constants import *

class StoreProtocol(AMP):

    @Transfer.responder
    def transfer(self, msg):
        #TODO: retrieve the file
        return {"msg": "server received msg"}

    @SendSingleImageInfo.responder
    def receive_image(self, user, store_name, image_name):
        from image_transfer_handler import fetch_image
        fetch_image(store_name, image_name, user, True)
        return {"success":True}

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