import unittest
from labot.utils import hash_id

class TestUtils(unittest.TestCase):
    def test_hash_id(self):
        self.assertEqual(hash_id('abc'), hash_id('abc'))
        self.assertNotEqual(hash_id('abc'), hash_id('def'))

if __name__ == '__main__':
    unittest.main()
