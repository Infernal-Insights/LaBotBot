import os
import unittest
from importlib.util import find_spec

if find_spec('pymongo') is not None:
    from labot.sync_to_mongo import _build_mongo_uri
else:
    _build_mongo_uri = None

class TestMongoURI(unittest.TestCase):
    def test_build_uri(self):
        if _build_mongo_uri is None:
            self.skipTest('pymongo not installed')
        os.environ['MONGODB_USERNAME'] = 'user'
        os.environ['MONGODB_PASSWORD'] = 'pass'
        os.environ['MONGODB_CLUSTER'] = 'cluster.example.com'
        os.environ['MONGODB_DATABASE'] = 'db'
        uri = _build_mongo_uri()
        self.assertIn('user', uri)
        self.assertIn('pass', uri)
        self.assertIn('cluster.example.com', uri)
        self.assertIn('db', uri)

if __name__ == '__main__':
    unittest.main()
