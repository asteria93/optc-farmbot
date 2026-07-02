"""
Tests for Flask app routes and API endpoints
"""
import unittest
import json
from app import create_app
from models import db


class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

        # Clear in-memory stores between tests
        import api.routes as api_routes
        api_routes.accounts_store.clear()
        api_routes.farming_sessions.clear()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

        import api.routes as api_routes
        api_routes.accounts_store.clear()
        api_routes.farming_sessions.clear()

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_list_accounts_empty(self):
        response = self.client.get('/api/accounts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('accounts', data)
        self.assertEqual(data['count'], 0)

    def test_create_account(self):
        payload = {'username': 'testuser', 'password': 'pass123', 'email': 'test@example.com'}
        response = self.client.post(
            '/api/accounts',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('account', data)
        self.assertEqual(data['account']['username'], 'testuser')

    def test_create_account_missing_fields(self):
        payload = {'email': 'test@example.com'}
        response = self.client.post(
            '/api/accounts',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_get_account(self):
        # Create first
        payload = {'username': 'testuser', 'password': 'pass123'}
        create_response = self.client.post(
            '/api/accounts',
            data=json.dumps(payload),
            content_type='application/json',
        )
        account_id = json.loads(create_response.data)['account']['id']

        # Retrieve
        response = self.client.get(f'/api/accounts/{account_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['account']['username'], 'testuser')

    def test_get_account_not_found(self):
        response = self.client.get('/api/accounts/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_delete_account(self):
        payload = {'username': 'testuser', 'password': 'pass123'}
        create_response = self.client.post(
            '/api/accounts',
            data=json.dumps(payload),
            content_type='application/json',
        )
        account_id = json.loads(create_response.data)['account']['id']

        response = self.client.delete(f'/api/accounts/{account_id}')
        self.assertEqual(response.status_code, 200)

    def test_start_farming(self):
        # Create account first
        payload = {'username': 'testuser', 'password': 'pass123'}
        create_response = self.client.post(
            '/api/accounts',
            data=json.dumps(payload),
            content_type='application/json',
        )
        account_id = json.loads(create_response.data)['account']['id']

        # Start farming
        farm_payload = {'account_id': account_id, 'mode': 'story'}
        response = self.client.post(
            '/api/farming/start',
            data=json.dumps(farm_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('session', data)

    def test_start_farming_invalid_account(self):
        payload = {'account_id': 'nonexistent', 'mode': 'story'}
        response = self.client.post(
            '/api/farming/start',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)

    def test_account_stats(self):
        response = self.client.get('/api/stats/accounts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_accounts', data)

    def test_farming_stats(self):
        response = self.client.get('/api/stats/farming')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_sessions', data)

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
