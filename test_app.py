import unittest
import requests
import redis
import app
import json

BASE = 'http://127.0.0.1:5000/'

class TestAPI(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_valid_package_and_version(self):
        response = requests.get(BASE + 'find-up/3.0.0')
        self.assertEqual(response.json()['deps'], {'locate-path': '^3.0.0'})

    def test_get_valid_namespace_package_and_version(self):
        response = requests.get(BASE + '@babel/types/^7.4.0')
        self.assertEqual(response.json()['devDeps'], {'@babel/generator': '^7.4.0', '@babel/parser': '^7.4.0'})

    def test_get_invalid_package(self):
        response = requests.get(BASE + 'qqqqqq/3.0.0')
        self.assertEqual(response.text, 'Not Found')

    def test_get_invalid_version(self):
        response = requests.get(BASE + 'find-up/100.100.100')
        self.assertEqual(response.text, 'version not found: 100.100.100')

    def test_get_invalid_name_space(self):
        response = requests.get(BASE + '@bbbbbbb/types/^7.4.0')
        self.assertEqual(response.text, 'Not Found')

    def test_clean_version(self):
        version = app.clean_version('^0.0.0')
        self.assertEqual(version, '0.0.0')

        version = app.clean_version('~0.0.0')
        self.assertEqual(version, '0.0.0')

        version = app.clean_version('>0.0.0')
        self.assertEqual(version, 'latest')

        version = app.clean_version('*')
        self.assertEqual(version, 'latest')

        version = app.clean_version('0.0.x')
        self.assertEqual(version, '0.0.0')


if __name__ == "__main__":
    unittest.main()