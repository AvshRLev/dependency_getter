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
        

if __name__ == "__main__":
    unittest.main()