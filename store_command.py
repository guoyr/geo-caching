from twisted.protocols import amp

class Transfer(amp.Command):
	arguments = [("msg",amp.String())]
    response = [('msg',amp.String())]
 