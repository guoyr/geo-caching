#main function for storage machines (east and west)
import sys

from twisted.internet import selectreactor
selectreactor.install
from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint

from factory_manager import FactoryManager
from image_transfer_handler import get_image_factory
from settings import *
from constants import *
def main():

    http_port = 8666

    #connection to client_db

    from twisted.internet import reactor
    image_transfer_endpoint = TCP4ServerEndpoint(reactor, http_port)
    image_transfer_endpoint.listen(get_image_factory())

    if SERVER_ID == COORDINATOR_ID:
        FactoryManager().start_coordinator_server()
    else:
        FactoryManager().start_store_server()

    # TODO: listen to HTTP and AMP server
    log.startLogging(sys.stdout)
    reactor.run()


if __name__ == '__main__':
    main()
