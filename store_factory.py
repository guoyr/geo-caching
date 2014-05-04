from twisted.protocols.amp import AMP
from twisted.internet.protocol import Factory
from store_command import *
class StoreProtocol(AMP):

	@Transfer.responder
	def transfer(self, msg):
		#TODO: download the file
		return {"msg": "server received msg"}





class StoreFactory(Factory):
	protocol=StoreProtocol