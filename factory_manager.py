import sys
sys.path.insert(0, "../")

from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint

from store_factory import StoreFactory
from coordinator_factory import CoordinatorFactory

from settings import *


class FactoryManager(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FactoryManager, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.client_db_loc = "clientdb-5412.cloudapp.net"
        
        self.store_server_loc = ""
        if SERVER_ID == "WEST":
            self.store_server_loc = "east-5412.cloudapp.net"
        elif SERVER_ID == "EAST":
            self.store_server_loc = "west-5412.cloudapp.net"


        self.store_amp_port = 8750
        self.coordinator_amp_port = 8760

        self.store_server_deferred = None
        self.clientdb_server_deferred = None


    def start_store_server(self):
        if not self.store_server_deferred:
            from twisted.internet import reactor
            self.store_server_deferred = TCP4ServerEndpoint(reactor, self.store_amp_port).listen(StoreFactory())
        return self.store_server_deferred


    def start_coordinator_server(self):
        if not self.clientdb_server_deferred:
            from twisted.internet import reactor
            self.clientdb_server_deferred = TCP4ServerEndpoint(reactor, self.coordinator_amp_port).listen(CoordinatorFactory())
        return self.clientdb_server_deferred

    def get_store_client_deferred(self, server_location=None):
        from twisted.internet import reactor
        if self.store_server_loc:
            return TCP4ClientEndpoint(reactor, self.store_server_loc, self.store_amp_port).connect(StoreFactory())
        else:
            return TCP4ClientEndpoint(reactor, server_location, self.store_amp_port).connect(StoreFactory())

    def get_coordinator_client_deferred(self):
        from twisted.internet import reactor
        return TCP4ClientEndpoint(reactor, self.client_db_loc, self.coordinator_amp_port).connect(CoordinatorFactory())




