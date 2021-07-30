import requests
import unittest
from unittest import mock
import main
import os
import redis
from main import extract_deps

redis_host = os.environ.get('REDIS', default='localhost')
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def mocked_get_from_node_api(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://registry.npmjs.org/find-up/3.0.0':
        return MockResponse({"dependencies":{"locate-path":"^6.0.0"},"devDependencies":{"ava":"^2.1.0"}}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)

class TestAPI(unittest.TestCase):
    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_happy_path(self, mock_get):
        # Arrange
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('find-up/3.0.0')

        # Act
        response = self.app.get('find-up/3.0.0')

        # Assert
        # Check response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'deps': {'locate-path': '^6.0.0'}, 'devDeps': {'ava': '^2.1.0'}})
        # Check correct path was called
        self.assertIn(mock.call('https://registry.npmjs.org/find-up/3.0.0'), mock_get.call_args_list)
        # Check response was cached
        self.assertEqual(main.get_from_cache('find-up/3.0.0')[0:30], '{"dependencies": {"locate-path')
        # Assert one call was made to mocked function
        self.assertEqual(len(mock_get.call_args_list), 1)

        # Act
        # Check next request comes from cache and mock_get is not called again
        second_call = self.app.get('find-up/3.0.0')

        # Assert
        self.assertEqual(second_call.status_code, 200)
        self.assertEqual(second_call.json, {'deps': {'locate-path': '^6.0.0'}, 'devDeps': {'ava': '^2.1.0'}})
        # Assert no other call was made to mocked function
        self.assertEqual(len(mock_get.call_args_list), 1)

if __name__ == "__main__":
    unittest.main()
