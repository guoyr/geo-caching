#main entry point for the coordinator (client db)
import sys

from twisted.internet import selectreactor
selectreactor.install

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint

from autobahn.twisted.websocket import WebSocketServerFactory

from measurement_handler import LatencyMeasurementProtocol

from factory_manager import FactoryManager

def main():

    from twisted.internet import reactor    

    http_measurement_port = 8888

    measurement_factory = WebSocketServerFactory()
    measurement_factory.protocol = LatencyMeasurementProtocol

    measurement_endpoint =  TCP4ServerEndpoint(reactor, http_measurement_port)
    measurement_endpoint.listen(measurement_factory)   

    FactoryManager().start_coordinator_server()

    log.startLogging(sys.stdout)
    reactor.run()

if __name__ == '__main__':
    main()