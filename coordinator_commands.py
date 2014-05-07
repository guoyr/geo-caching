from twisted.protocols import amp
from constants import *

class FetchData(amp.Command):
    arguments = [("msg",amp.String())]
    response = [('msg',amp.String())]

class AddAccessRecord(amp.Command):
	arguments = [(USER_UID_KEY, amp.String()), (PREFERRED_STORE_KEY, amp.String()), (IS_SAVE_ACTION, amp.Boolean())]
	response = [("success", amp.Boolean())]

class GetMaster(amp.Command):
    arguments = [(USER_UID_KEY,amp.String())]
    response = [(MASTER_SERVER_ID,amp.String())]