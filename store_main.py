#main function for storage machines (east and west)
import sys

from twisted.internet import selectreactor
selectreactor.install
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from store_factory import StoreFactory

from image_transfer_handler import get_image_factory

def main():
    server_loc = "east-5412.cloudapp.net"           # location of the server connecting to, change it to west-5412.cloudapp.net for machine on east
    client_db_loc = "clientdb-5412.cloudapp.net"    # location of the clientdb machine

    amp_port = 8750                               # port that is open for amp communication
    http_port = 8666

    client_endpoint = TCP4ClientEndpoint(reactor, server_loc, amp_port)
    server_endpoint = TCP4ServerEndpoint(reactor, amp_port)

    #connection to client_db
    client_db_server_endpoint = TCP4ServerEndpoint(reactor, amp_port)
    client_db_client_endpoint = TCP4ClientEndpoint(reactor, client_db_loc, amp_port)


    store_factory = StoreFactory()
    server_deferred = server_endpoint.listen(store_factory)
    client_deferred = client_endpoint.connect(store_factory)

    image_transfer_endpoint = TCP4ServerEndpoint(reactor, http_port)
    image_transfer_endpoint.listen(get_image_factory())

    # TODO: listen to HTTP and AMP server
    log.startLogging(sys.stdout)
    reactor.run()

if __name__ == '__main__':
    main()
