from collections import defaultdict


IMAGE_UID_KEY = "image_uid_key"
USER_UID_KEY = "user_id"
LATENCY_DICT_KEY = "latency_dict_key"
CACHE_UID_KEY = "cache_uid"

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

HTTP_PORT = 8666
HTTP_MEASUREMENT_PORT = 8888

#LRU cache for latency
LatencyCache = defaultdict(list)