from twisted.protocols import amp
from pymongo import errors

from constants import *

class FetchData(amp.Command):
    arguments = [("msg",amp.String())]
    response = [('msg',amp.String())]

class AddAccessRecord(amp.Command):
    arguments = [(IMAGE_UID_KEY, amp.String()), (USER_UID_KEY, amp.String()), (PREFERRED_STORE_KEY, amp.String()), (LATENCY_KEY, amp.Float()), (FROM_KEY, amp.String()), (TO_KEY, amp.String())]
    response = [("success", amp.Boolean())]

class GetMaster(amp.Command):
    arguments = [(USER_UID_KEY,amp.String()), (PREFERRED_STORE_KEY, amp.String())]
    response = [(MASTER_SERVER_ID,amp.String())]
    errors = {errors.ConnectionFailure: 'DB_CONNECTION_ERROR'}