#handles image transfers
from twisted.web.resource import Resource
from twisted.web.server import Site
import json

class MeasurementResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        result = {"east_latency":"1.004", "west_latency":"2.056"}
        print "measurement get"
        return json.dumps(result)

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