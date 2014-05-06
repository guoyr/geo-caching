#handles image transfers
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet.task import LoopingCall

from autobahn.twisted.websocket import WebSocketServerProtocol

import json

class LatencyMeasurementProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print "Client connecting: {0}".format(request.peer)
        lc = LoopingCall(self.sendLatencyInfo,None)
        lc.start(10)

    def onOpen(self):
        print "WebSocket connection open."

    def onMessage(self, payload, isBinary):
        if isBinary:
            print "Binary message received: {0} bytes".format(len(payload))
        else:
            print "Text message received: {0}".format(payload.decode('utf8'))
        self.sendMessage(json.dumps(payload), isBinary)

    def sendLatencyInfo(self, latency_dict):
        print "send latency info"
        latency_dict = {"east_latency":"1.004", "west_latency":"2.056"}
        self.sendMessage(json.dumps(latency_dict), False)

    def onClose(self, wasClean, code, reason):
        print "WebSocket connection closed: {0}".format(reason)

class MeasurementResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        result = {"east_latency":"1.004", "west_latency":"2.056"}
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