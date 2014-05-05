#handles image transfers
from twisted.web.resource import Resource
from twisted.web.server import Site


class ImageTransferResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        print "client image get"
        return "client image get"

    def render_POST(self, request):
        print "client image post"
        return "client image post"

def get_image_factory():
    resource = Resource()
    resource.putChild('upload_image', ImageTransferResource())
    factory = Site(resource)
    return factory