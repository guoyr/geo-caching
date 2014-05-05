#main entry point for the coordinator (client db)
from twisted.internet import reactor

def main():

    # TODO: listen to HTTP and AMP server
    reactor.run()

if __name__ == '__main__':
    main()