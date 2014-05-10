from twisted.protocols import amp

from constants import *

class Transfer(amp.Command):
    arguments = [("msg",amp.ListOf(amp.String()))]
    response = [('msg',amp.String())]

class SendSingleImageInfo(amp.Command):
    arguments = [(USER_UID_KEY, amp.String()), (CACHE_UID_KEY, amp.String()), (IMAGE_UID_KEY, amp.String())]
    response = [("success", amp.Boolean())]

class PrepareMasterChange(amp.Command):
    arguments = [(IS_NEW_MASTER, amp.Boolean()), (USER_UID_KEY, amp.String())]
    response = [("prepared", amp.Boolean())]