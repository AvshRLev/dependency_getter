import json
import os
import redis

redis_host = os.environ.get('REDIS', default='localhost')
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def cache_for_one_day(path_string, response):
    redis_client.setex(path_string , 86400, json.dumps(response.json()))

def get_from_cache(path_string):
    return redis_client.get(path_string)
