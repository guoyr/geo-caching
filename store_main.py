#main function for storage machines (east and west)
from twisted.internet import selectreactor
selectreactor.install
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint

def main():

	# TODO: listen to HTTP and AMP server
	reactor.run()

if __name__ == '__main__':
	main()