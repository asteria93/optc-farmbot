"""
Tests for OPTC Farming Bot
"""
import unittest
from bot.account_manager import AccountManager, AccountAuthenticator
from bot.farmer import Farmer, FarmingMode, FarmingStrategy

class TestAccountManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = AccountManager(None)
    
    def test_create_account(self):
        account = self.manager.create_account('testuser', 'test@example.com', 'password123')
        self.assertIsNotNone(account['id'])
        self.assertEqual(account['username'], 'testuser')
        self.assertEqual(account['level'], 1)
    
    def test_get_account(self):
        created = self.manager.create_account('testuser', 'test@example.com', 'password123')
        retrieved = self.manager.get_account(created['id'])
        self.assertEqual(retrieved['username'], 'testuser')
    
    def test_list_accounts(self):
        self.manager.create_account('user1', 'user1@example.com', 'pass1')
        self.manager.create_account('user2', 'user2@example.com', 'pass2')
        accounts = self.manager.list_accounts()
        self.assertEqual(len(accounts), 2)
    
    def test_delete_account(self):
        account = self.manager.create_account('testuser', 'test@example.com', 'password123')
        deleted = self.manager.delete_account(account['id'])
        self.assertTrue(deleted)
        self.assertIsNone(self.manager.get_account(account['id']))


class TestFarmer(unittest.TestCase):
    
    def setUp(self):
        self.account_data = {
            'id': 'test123',
            'username': 'testuser',
            'level': 1,
            'berry': 0,
            'gold': 0,
            'experience': 0,
            'farming_stats': {'story_chapters': 0, 'events_completed': 0, 'missions_completed': 0, 'total_runs': 0},
        }
        self.farmer = Farmer('test123', self.account_data)
    
    def test_start_farming(self):
        session = self.farmer.start_farming(FarmingMode.STORY, FarmingStrategy.MODERATE)
        self.assertTrue(self.farmer.farming_active)
        self.assertEqual(session['mode'], 'story')
    
    def test_farm_story(self):
        self.farmer.start_farming()
        rewards = self.farmer.farm_story(1)
        self.assertIn('berries', rewards)
        self.assertGreater(rewards['berries'], 0)
    
    def test_get_farming_status(self):
        self.farmer.start_farming()
        status = self.farmer.get_farming_status()
        self.assertTrue(status['farming_active'])
        self.assertEqual(status['account_id'], 'test123')


class TestAccountAuthenticator(unittest.TestCase):
    
    def setUp(self):
        self.auth = AccountAuthenticator()
    
    def test_authenticate(self):
        token = self.auth.authenticate('testuser', 'password')
        self.assertIsNotNone(token)
    
    def test_verify_session(self):
        token = self.auth.authenticate('testuser', 'password')
        self.assertTrue(self.auth.verify_session(token))
    
    def test_logout(self):
        token = self.auth.authenticate('testuser', 'password')
        logged_out = self.auth.logout(token)
        self.assertTrue(logged_out)
        self.assertFalse(self.auth.verify_session(token))


if __name__ == '__main__':
    unittest.main()
