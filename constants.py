from collections import defaultdict


IMAGE_UID_KEY = "image_uid_key"
USER_UID_KEY = "user_uid_key"
LATENCY_DICT_KEY = "latency_dict_key"
CACHE_UID_KEY = "cache_uid_key"

MASTER_SERVER_ID = "master_server_id"

WEST_STORE_ID = "west_store_id"
EAST_STORE_ID = "east_store_id"
COORDINATOR_ID = "coordinator_id"
CLIENT_ID = "client_id"

CLIENT_LATENCY_EAST_KEY = "latency_east"
LATENCY_KEY = "latency_key"

FROM_KEY = "from_key"
TO_KEY = "to_key"

PREFERRED_STORE_KEY = "preferred_store"
IS_CLIENT_KEY = "is_client"
IS_SAVE_ACTION = "is_save"


IS_NEW_MASTER = "is_new_master"

HTTP_PORT = 8666
HTTP_MEASUREMENT_PORT = 8888

TIMEOUT = 10
SERVER_LATENCY = 90

CACHE_SIZE = 5

#LRU cache for latency
LatencyCache = defaultdict(list)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'