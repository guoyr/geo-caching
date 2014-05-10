#handles image transfers
import json
import random

from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet.task import LoopingCall

from autobahn.twisted.websocket import WebSocketServerProtocol

from constants import *

class LatencyMeasurementProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print "Client connecting: {0}".format(request.peer)
        self.lc = LoopingCall(self.sendLatencyInfo)
        self.lc.start(3)

    def onOpen(self):
        print "WebSocket connection open."

    def onMessage(self, payload, isBinary):
        if isBinary:
            print "Binary message received: {0} bytes".format(len(payload))
        else:
            print "Text message received: {0}".format(payload.decode('utf8'))
        self.sendMessage(json.dumps(payload), isBinary)

    def sendLatencyInfo(self):
        print "send latency info"
        locs_dict = {"EAST":"ep","WEST":"wp","CLIENT":"user_point"}
        

        from twisted.internet import reactor

        callTime = 0
        for userID in LatencyCache.keys():
            for from_key, to_key, latency in LatencyCache[userID]:
                pass

        self.sendMessage(json.dumps(), False)

    def onClose(self, wasClean, code, reason):
        print "WebSocket connection closed: {0}".format(reason)

class MeasurementResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        result = {"east_latency":"1.004", "west_latency":"2.056", "user_location_x":""}
        print "measurement get"
        return json.dumps([result])

    def render_POST(self, request):
        request.setHeader("content-type", "application/json")
        result = {"east_latency":"1.004", "west_latency":"2.056"}
        print "measurement post"
        return json.dumps(result)

def get_measurement_factory():
    resource = Resource()
    resource.putChild('measurement', MeasurementResource())
    factory = Site(resource)
    return factory