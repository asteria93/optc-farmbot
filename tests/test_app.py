import unittest
from unittest.mock import patch

from app import create_app
from models import Account, FarmSession, db


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'FARMING_TASK_MODE': 'inline',
            'FARMING_LOOP_SLEEP_SECONDS': 0,
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_account(self, username='luffy'):
        response = self.client.post('/api/accounts', json={
            'username': username,
            'password': 'gumgum',
            'platform': 'android',
            'version': 'gb',
            'farming_config': {
                'auto_sell': True,
                'refill_strategy': 'skip',
                'farming_content': ['gifts', 'story', 'events', 'missions', 'auto_sell'],
            },
        })
        self.assertEqual(response.status_code, 201)
        return response.get_json()['account']

    def test_account_crud_endpoints(self):
        created = self._create_account()
        list_response = self.client.get('/api/accounts')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.get_json()['count'], 1)

        details = self.client.get(f"/api/accounts/{created['id']}")
        self.assertEqual(details.status_code, 200)
        self.assertEqual(details.get_json()['account']['username'], 'luffy')

        update = self.client.put(f"/api/accounts/{created['id']}", json={
            'platform': 'ios',
            'version': 'jp',
            'farming_config': {
                'auto_sell': False,
                'refill_strategy': 'gems',
                'farming_content': ['story', 'events'],
            },
        })
        self.assertEqual(update.status_code, 200)
        payload = update.get_json()['account']
        self.assertEqual(payload['platform'], 'ios')
        self.assertEqual(payload['farming_config']['refill_strategy'], 'gems')

        delete = self.client.delete(f"/api/accounts/{created['id']}")
        self.assertEqual(delete.status_code, 200)
        self.assertEqual(self.client.get('/api/accounts').get_json()['count'], 0)

    def test_farming_flow_persists_sessions_logs_and_stats(self):
        created = self._create_account('zoro')
        response = self.client.post('/api/farming/start', json={
            'account_id': created['id'],
            'duration': 0,
            'farming_mode': 'balanced',
        })
        self.assertEqual(response.status_code, 202)

        status = self.client.get(f"/api/farming/status/{created['id']}")
        self.assertEqual(status.status_code, 200)
        status_payload = status.get_json()
        self.assertEqual(status_payload['account']['farming_status'], 'idle')
        self.assertEqual(status_payload['current_session']['status'], 'completed')

        sessions = self.client.get(f"/api/farming/sessions/{created['id']}")
        self.assertEqual(sessions.status_code, 200)
        self.assertEqual(sessions.get_json()['count'], 1)
        self.assertGreaterEqual(sessions.get_json()['sessions'][0]['items_collected'], 1)

        logs = self.client.get(f"/api/farming/logs/{created['id']}")
        self.assertEqual(logs.status_code, 200)
        self.assertGreaterEqual(logs.get_json()['count'], 5)

        stats = self.client.get('/api/stats')
        self.assertEqual(stats.status_code, 200)
        stats_payload = stats.get_json()
        self.assertEqual(stats_payload['total_accounts'], 1)
        self.assertEqual(stats_payload['total_sessions'], 1)
        self.assertGreater(stats_payload['total_items_collected'], 0)

    def test_stop_endpoint_marks_active_session(self):
        created = self._create_account('sanji')
        account = db.session.get(Account, created['id'])
        session = FarmSession(account_id=account.id, farming_mode='events', duration_hours=4, status='running')
        account.is_farming = True
        account.farming_status = 'running'
        db.session.add(session)
        db.session.commit()

        response = self.client.post(f"/api/farming/stop/{created['id']}")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()['session']
        self.assertTrue(payload['stop_requested'])
        self.assertEqual(payload['status'], 'stopping')

    def test_dashboard_and_account_pages_render(self):
        created = self._create_account('nami')
        dashboard = self.client.get('/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn(b'Account Dashboard', dashboard.data)
        details = self.client.get(f"/account/{created['id']}")
        self.assertEqual(details.status_code, 200)
        self.assertIn(b'Account nami', details.data)

    def test_farming_failure_is_logged_and_session_marked_failed(self):
        created = self._create_account('ace')
        with patch('tasks._authenticate_account', side_effect=RuntimeError('login failed')):
            response = self.client.post('/api/farming/start', json={
                'account_id': created['id'],
                'duration': 0,
                'farming_mode': 'balanced',
            })
        self.assertEqual(response.status_code, 202)

        status = self.client.get(f"/api/farming/status/{created['id']}")
        payload = status.get_json()
        self.assertEqual(payload['account']['farming_status'], 'error')
        self.assertEqual(payload['account']['last_error'], 'login failed')
        self.assertEqual(payload['current_session']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
