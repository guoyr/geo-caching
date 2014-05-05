#main entry point for the coordinator (client db)
from twisted.internet import reactor
from image_transfer_hander import get_image_handler

def main():

    # TODO: listen to HTTP and AMP server
    reactor.run()

if __name__ == '__main__':
    main()