import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestLaunchFiles(unittest.TestCase):
    def test_required_launch_scripts_exist(self):
        for relative_path in (
            'setup.bat',
            'setup.sh',
            'start.bat',
            'start.sh',
            'stop.bat',
            'stop.sh',
            'celery_app.py',
            'app.py',
        ):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_requirements_include_launch_dependencies(self):
        requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8').lower()
        for package in (
            'flask',
            'flask-sqlalchemy',
            'celery',
            'redis',
            'cryptography',
            'requests',
        ):
            self.assertIn(package, requirements)

    def test_setup_scripts_install_and_init_database(self):
        setup_sh = (ROOT / 'setup.sh').read_text(encoding='utf-8')
        setup_bat = (ROOT / 'setup.bat').read_text(encoding='utf-8')

        self.assertIn('pip install -r requirements.txt', setup_sh)
        self.assertIn('pip install -r requirements.txt', setup_bat)
        self.assertIn('create_app()', setup_sh)
        self.assertIn('create_app()', setup_bat)

    def test_start_scripts_launch_all_services(self):
        start_sh = (ROOT / 'start.sh').read_text(encoding='utf-8')
        start_bat = (ROOT / 'start.bat').read_text(encoding='utf-8')

        self.assertIn('redis-server', start_sh)
        self.assertIn('celery -A celery_app worker --loglevel=info', start_sh)
        self.assertIn('app.py', start_sh)
        self.assertIn('http://localhost:5000', start_sh)

        self.assertIn('redis-server', start_bat)
        self.assertIn('celery -A celery_app worker --loglevel=info', start_bat)
        self.assertIn('app.py', start_bat)
        self.assertIn('http://localhost:5000', start_bat)

    def test_readme_has_simple_launch_steps(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('WINDOWS:', readme)
        self.assertIn('Double-clic `setup.bat`', readme)
        self.assertIn('MAC/LINUX:', readme)
        self.assertIn('bash setup.sh', readme)


if __name__ == '__main__':
    unittest.main()
