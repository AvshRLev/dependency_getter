from flask.wrappers import Response
import time
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
    elif args[0] == 'https://registry.npmjs.org/@namespace/find-up/3.0.0':
        return MockResponse({"dependencies":{"locate-path":"^6.0.0"},"devDependencies":{"ava":"^2.1.0"}}, 200)
    elif args[0] == 'https://registry.npmjs.org/somethingweird/3.0.0':
        return MockResponse({"dependencies":{100:100},"devDependencies":{True:"^^^^^^"}}, 256)
    if args[0] == 'https://registry.npmjs.org/request-too-long/3.0.0':
        time.sleep(1)
        return MockResponse({"dependencies":{"locate-path":"^6.0.0"},"devDependencies":{"ava":"^2.1.0"}}, 200)
    return MockResponse(None, 404)

class TestAPI(unittest.TestCase):


    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_get_package(self, mock_get):
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

    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_get_package_with_namespace(self, mock_get):
        # Arrange
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('@namespace/find-up/3.0.0')

        # Act
        response = self.app.get('@namespace/find-up/3.0.0')

        # Assert
        # Check response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'deps': {'locate-path': '^6.0.0'}, 'devDeps': {'ava': '^2.1.0'}})
        # Check correct path was called
        self.assertIn(mock.call('https://registry.npmjs.org/@namespace/find-up/3.0.0'), mock_get.call_args_list)
        # Check response was cached
        self.assertEqual(main.get_from_cache('find-up/3.0.0')[0:30], '{"dependencies": {"locate-path')
        # Assert one call was made to mocked function
        self.assertEqual(len(mock_get.call_args_list), 1)

        # Act
        # Check next request comes from cache and mock_get is not called again
        second_call = self.app.get('@namespace/find-up/3.0.0')

        # Assert
        self.assertEqual(second_call.status_code, 200)
        self.assertEqual(second_call.json, {'deps': {'locate-path': '^6.0.0'}, 'devDeps': {'ava': '^2.1.0'}})
        # Assert no other call was made to mocked function
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_non_existing_package(self, mock_get):
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('non-existent-package/3.3.3')
        response = self.app.get('non-existent-package/3.3.3')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'This has returned None')

    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_weird_return_value_package(self, mock_get):
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('somethingweird/3.0.0')
        response = self.app.get('somethingweird/3.0.0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'deps': {'100': 100}, 'devDeps': {'true': '^^^^^^'}})

    @mock.patch('main.get_from_node_api', side_effect=mocked_get_from_node_api)
    def test_request_takes_too_long(self, mock_get):
        main.app.testing = True
        self.app = main.app.test_client()
        redis_client.delete('request-too-long/3.0.0')
        response = self.app.get('request-too-long/3.0.0')
        with self.subTest(msg='Response Status Code '):
            self.assertEqual(response.status_code, 500)
        with self.subTest(msg='Response Message'):
            self.assertEqual(response.json, "Request Timeout Error")
        with self.subTest(msg='Response Took Longer Than 0.8 Seconds'):
            self.assertGreater(response.elapsed.total_seconds(), 0.8)
    

    
class TestUnits(unittest.TestCase):

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
    
    @mock.patch('main.requests.get')
    def test_get_from_node_api_ok(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json_data = "Ok"
        response = main.get_from_node_api('abc/123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_data, 'Ok')

    @mock.patch('main.requests.get')
    def test_get_from_node_api_not_ok(self, mock_get):
        mock_get.return_value.status_code = 404
        response = main.get_from_node_api('abc/123')
        self.assertEqual(response.status_code, 404)
        

class TestIndexRoute(unittest.TestCase):
    def test_home(self):
        tester = main.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<!DOCTYPE html>\n<html>\n  <head> \n'  in response.data)
        
    def test_other(self):
        tester = main.app.test_client(self)
        response = tester.get('a', content_type='html/text')
        self.assertEqual(response.status_code, 404)
        self.assertTrue( b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML' in response.data)
        
if __name__ == "__main__":
    unittest.main()
