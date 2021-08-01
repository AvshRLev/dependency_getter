import json

def cache_for_one_day(path_string, response, redis_client):
    redis_client.setex(path_string , 86400, json.dumps(response.json()))

def get_from_cache(path_string, redis_client):
    return redis_client.get(path_string)
