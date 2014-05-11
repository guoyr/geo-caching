from twisted.protocols import amp

from constants import *

class SendSingleImageInfo(amp.Command):
    arguments = [(USER_UID_KEY, amp.String()), (CACHE_UID_KEY, amp.String()), (IMAGE_UID_KEY, amp.String())]
    response = [("success", amp.Boolean())]

#inform new master of master change
class InitiateMasterChange(amp.Command):
    arguments = [(USER_UID_KEY, amp.String()), ("old_master_key", amp.String())]
    response = [("ack", amp.Boolean())]

#new master issue this command to old master
class SendAllImages(amp.Command):
	arguments = [(USER_UID_KEY, amp.String())]
	response = [("image_info_list", amp.ListOf(amp.String()))]

#new master issue to old master to indicate master transfer is complete
class FinishMasterTransfer(amp.Command):
	arguments = [(USER_UID_KEY, amp.String())]
	response = [("success", amp.Boolean())]
