import unittest
from unittest import mock
from unittest.mock import Mock, patch
import requests
import redis
import main
import json
from main import get_from_cache, get_from_node_api


redis_host = 'localhost'
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

BASE = 'http://127.0.0.1:5000/'



class TestAPI(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('find-up/3.0.0')
        

    def tearDown(self):
        pass

    mock_response = json.dumps({"name":"@types/ms","version":"0.7.31","description":"TypeScript definitions for ms", "dependencies": "{'locate-path': '^3.0.0'}"})
    
    @patch('main.get_from_node_api')
    def test_get_from_node_api(self, mock_get_from_node):
        mock_cache = [{"name":"lodash","version":"4.8.0"}]
        mock_get_from_node.return_value = Mock(ok=True)
        mock_get_from_node.status_code = 200
        mock_get_from_node.return_value.json.return_value = mock_cache
        response = self.app.get(BASE + 'find/3.0.0')
        self.assertEqual(response, mock_cache)
    

    # @patch('main.get_from_cache')
    # def test_get_from_cache(self, mock_get_from_cache):
    #     mock_cache = '{"name":"lodash","version":"4.8.0"}'
    #     mock_get_from_cache.return_value.ok = True
    #     mock_get_from_cache.return_value.json.return_value = mock_cache
    #     response = self.app.get(BASE + 'find/3.0.0')
    #     self.assertEqual(response, json.dumps(mock_cache))
        
    
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

    def test_clean_version(self):
        version = main.clean_version('^0.0.0')
        self.assertEqual(version, '0.0.0')

        version = main.clean_version('~0.0.0')
        self.assertEqual(version, '0.0.0')

        version = main.clean_version('>0.0.0')
        self.assertEqual(version, 'latest')

        version = main.clean_version('*')
        self.assertEqual(version, 'latest')

        version = main.clean_version('0.0.x')
        self.assertEqual(version, '0.0.0')


if __name__ == "__main__":
    unittest.main()