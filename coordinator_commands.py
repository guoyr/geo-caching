from twisted.protocols import amp

class FetchData(amp.Command):
    arguments = [("msg",amp.String())]
    response = [('msg',amp.String())]

class GetMaster(amp.Command):
    arguments = [("msg",amp.ListOf(amp.String()))]
    response = [('msg',amp.String())]

