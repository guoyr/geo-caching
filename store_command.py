from twisted.protocols import amp

class Transfer(amp.Command):
    arguments = [("msg",amp.ListOf(amp.String()))]
    response = [('msg',amp.String())]
 