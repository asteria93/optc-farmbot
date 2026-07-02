import unittest

from app import create_app
from models import db


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'CELERY_TASK_ALWAYS_EAGER': True,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_routes(self):
        for route in ['/', '/dashboard', '/accounts', '/farming', '/settings', '/logs']:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, route)

    def test_account_creation_and_listing(self):
        response = self.client.post('/api/accounts', json={
            'username': 'web-user',
            'email': 'web-user@example.com',
            'password': 'secret',
        })
        self.assertEqual(response.status_code, 201)
        created = response.get_json()['account']

        listing = self.client.get('/api/accounts')
        self.assertEqual(listing.status_code, 200)
        payload = listing.get_json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['accounts'][0]['id'], created['id'])

    def test_start_farming_records_session_and_logs(self):
        created = self.client.post('/api/accounts', json={
            'username': 'farmer',
            'email': 'farmer@example.com',
            'password': 'secret',
        }).get_json()['account']

        response = self.client.post('/api/farming/start', json={
            'account_id': created['id'],
            'mode': 'all',
            'strategy': 'moderate',
            'run_immediately': True,
        })
        self.assertEqual(response.status_code, 202)
        session = response.get_json()['session']
        self.assertEqual(session['status'], 'completed')
        self.assertEqual(session['total_runs'], 4)

        status = self.client.get(f"/api/farming/status/{session['id']}")
        self.assertEqual(status.status_code, 200)
        status_payload = status.get_json()
        self.assertGreaterEqual(status_payload['account_stats']['berry'], 25)
        self.assertGreaterEqual(len(status_payload['logs']), 1)

        stats = self.client.get('/api/stats/farming')
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.get_json()['total_runs'], 4)
