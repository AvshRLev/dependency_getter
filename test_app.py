import unittest
import requests
import redis
import main
import json

BASE = 'http://127.0.0.1:5000/'

class TestAPI(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def tearDown(self):
        pass

    def test_get_valid_package_and_version(self):
        response = self.app.get(BASE + 'find-up/3.0.0')
        self.assertEqual(response.get_json()['deps'], {'locate-path': '^3.0.0'})

    def test_get_valid_namespace_package_and_version(self):
        response = self.app.get(BASE + '@babel/types/^7.4.0')
        self.assertEqual(response.get_json()['devDeps'], {'@babel/generator': '^7.4.0', '@babel/parser': '^7.4.0'})

    def test_get_invalid_package(self):
        response = self.app.get(BASE + 'qqqqqq/3.0.0')
        self.assertEqual(response.get_data(), b'Not Found')

    def test_get_invalid_version(self):
        response = self.app.get(BASE + 'find-up/100.100.100')
        self.assertEqual(response.get_data(), b'version not found: 100.100.100')

    def test_get_invalid_name_space(self):
        response = self.app.get(BASE + '@bbbbbbb/types/^7.4.0')
        self.assertEqual(response.get_data(), b'Not Found')

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