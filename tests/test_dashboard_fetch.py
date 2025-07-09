import unittest
from unittest import mock
import sys
import types

# Provide a stub redis module so dashboard can be imported without Redis installed
sys.modules.setdefault('redis', types.SimpleNamespace(Redis=lambda *a, **k: None))
import importlib.machinery
pymongo_stub = types.ModuleType('pymongo')
pymongo_stub.__spec__ = importlib.machinery.ModuleSpec('pymongo', None)
sys.modules.setdefault('pymongo', pymongo_stub)
sys.modules.setdefault('dotenv', types.ModuleType('dotenv'))
sys.modules['dotenv'].load_dotenv = lambda *a, **k: None
import dashboard

class TestFetchProducts(unittest.TestCase):
    def test_fallback_called(self):
        with mock.patch('dashboard.get_all_products', side_effect=[[], ['p']]) as gap, \
             mock.patch('dashboard.sync_from_mongo_to_redis') as sync:
            result = dashboard.fetch_products()
            self.assertEqual(result, ['p'])
            sync.assert_called_once()
            self.assertEqual(gap.call_count, 2)

    def test_blank_items_filtered(self):
        products = [
            {'name': '', 'price': ''},
            {'name': 'A', 'price': '10'},
            {'name': '', 'price': '5'},
            {'name': 'B', 'price': ''},
        ]
        with mock.patch('dashboard.get_all_products', return_value=products):
            result = dashboard.fetch_products()
        self.assertEqual(result, [
            {'name': 'A', 'price': '10'},
            {'name': '', 'price': '5'},
            {'name': 'B', 'price': ''},
        ])

if __name__ == '__main__':
    unittest.main()
