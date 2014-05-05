#main entry point for the coordinator (client db)
import sys

from twisted.internet import selectreactor
selectreactor.install
from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from measurement_handler import get_measurement_factory
def main():

    from twisted.internet import reactor    

    http_measurement_port = 8888

    measurement_endpoint =  TCP4ServerEndpoint(reactor, http_measurement_port)
    measurement_endpoint.listen(get_measurement_factory())

    log.startLogging(sys.stdout)
    reactor.run()

if __name__ == '__main__':
    main()