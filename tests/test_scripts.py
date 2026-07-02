import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestStartupScripts(unittest.TestCase):
    def test_required_files_exist(self):
        required_files = [
            REPO_ROOT / 'setup_environment.bat',
            REPO_ROOT / 'setup_environment.sh',
            REPO_ROOT / 'QUICK_START.txt',
            REPO_ROOT / 'celery_app.py',
            REPO_ROOT / 'scripts' / 'start_bot.bat',
            REPO_ROOT / 'scripts' / 'start_bot.sh',
        ]

        for file_path in required_files:
            with self.subTest(file=file_path.name):
                self.assertTrue(file_path.exists())

    def test_setup_scripts_reference_requirements_and_db_init(self):
        for relative_path in ('setup_environment.bat', 'setup_environment.sh'):
            content = (REPO_ROOT / relative_path).read_text(encoding='utf-8')
            with self.subTest(file=relative_path):
                self.assertIn('requirements.txt', content)
                self.assertIn('scripts/init_db.py', content.replace('\\', '/'))

    def test_start_scripts_reference_redis_celery_flask_and_browser(self):
        expectations = {
            'scripts/start_bot.bat': [
                'redis-server',
                'celery -A celery_app:celery_app worker',
                'app.py',
                'http://localhost:5000',
            ],
            'scripts/start_bot.sh': [
                'redis-server',
                'celery -A celery_app:celery_app worker',
                'app.py',
                'http://localhost:5000',
            ],
        }

        for relative_path, snippets in expectations.items():
            content = (REPO_ROOT / relative_path).read_text(encoding='utf-8')
            for snippet in snippets:
                with self.subTest(file=relative_path, snippet=snippet):
                    self.assertIn(snippet, content)

    def test_quick_start_instructions_match_expected_text(self):
        expected = (
            'POUR WINDOWS:\n'
            '1. Double-clic setup_environment.bat\n'
            '2. Double-clic start_bot.bat\n'
            '3. Ouvre http://localhost:5000\n\n'
            'POUR MAC/LINUX:\n'
            '1. bash setup_environment.sh\n'
            '2. bash start_bot.sh\n'
            '3. Ouvre http://localhost:5000\n'
        )
        content = (REPO_ROOT / 'QUICK_START.txt').read_text(encoding='utf-8')
        self.assertEqual(content, expected)


if __name__ == '__main__':
    unittest.main()
