import unittest
from unittest import mock
from unittest.mock import Mock, patch
import os
import redis
import server
import json

redis_host = os.environ.get('REDIS', default='localhost')
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

BASE = 'http://127.0.0.1:5000/'

class TestAPI(unittest.TestCase):
    def setUp(self):
        server.app.testing = True
        self.app = server.app.test_client()
        redis_client.delete('find-up/3.0.0')
    
    def test_get_valid_package_and_version(self):
        response = self.app.get(BASE + 'find-up/3.0.0')
        self.assertEqual(response.get_json()['deps'], {'locate-path': '^3.0.0'})

    def test_get_valid_namespace_package_and_version(self):
        response = self.app.get(BASE + '@babel/types/^7.4.0')
        self.assertEqual(response.get_json()['devDeps'], {'@babel/generator': '^7.4.0', '@babel/parser': '^7.4.0'})

    def test_get_invalid_package(self):
        response = self.app.get(BASE + 'qqqqqq/3.0.0')
        self.assertEqual(response.get_json(), {'code': 404, 'response': 'Not Found'} )

    def test_get_invalid_version(self):
        response = self.app.get(BASE + 'find-up/100.100.100')
        self.assertEqual(response.get_json(), {'code': 404, 'response': 'version not found: 100.100.100'})

    def test_get_invalid_name_space(self):
        response = self.app.get(BASE + '@bbbbbbb/types/^7.4.0')
        self.assertEqual(response.get_json(),  {'code': 404, 'response': 'Not Found'} )

if __name__ == "__main__":
    unittest.main()