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
        self.prevUserX = -95.3831
        self.prevUserY = 29.7628
        self.lc = LoopingCall(self.sendLatencyInfo)
        self.lc.start(3)

    def onOpen(self):
        print "WebSocket connection open."

    def onMessage(self, payload, isBinary):
        if isBinary:
            print "Binary message received: {0} bytes".format(len(payload))
        else:
            print "Text message received: {0}".format(payload.decode('utf8'))
        # self.sendMessage(json.dumps(payload), isBinary)

    def sendLatencyInfo(self):
        print "in send latency info"
        locs_dict = {"EAST":"ep","WEST":"wp","CLIENT":"user_point"}
        # hack to determine usr location

        from twisted.internet import reactor

        for userID in LatencyCache.keys():
            callTime = 0.0
            print "send latency for user: "  + userID
            for from_key, to_key, latency in LatencyCache[userID]:
                print "animation from " + from_key + "to " + to_key + "latency " + str(latency)
                info = {}
                x, y = self._getUserCoords(from_key, to_key)
                #use tokey to determine from key
                info[FROM_KEY] = locs_dict[from_key]
                info[TO_KEY] = locs_dict[to_key]
                info["latency"] = str(latency)
                info["user_x"] = str(x)
                info["user_y"] = str(y)
                reactor.callLater(callTime, self.sendMessage, json.dumps(info), False)
                callTime += latency/100
        LatencyCache.clear()

    def _getUserCoords(self, from_key, to_key):
        #seattle and ithaca
        user_coords = {"WEST":[-122.3331,47.6097], "EAST": [-76.5000, 42.4433]}
        server = ""
        if "CLIENT" == from_key: server = to_key 
        elif "CLIENT" == to_key: server = from_key

        if server:
            x = user_coords[server][0]
            y = user_coords[server][1]

            self.prevUserY = y
            self.prevUserX = x

        return self.prevUserX, self.prevUserY

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