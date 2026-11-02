"""Local startup checks with an isolated database and no external services."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient
from streamlit.testing.v1 import AppTest

import data.storage as storage
from server import app


class LocalStartupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = patch.object(storage, 'DB_PATH', Path(self.temp.name) / 'test.db')
        self.db.start()

    def tearDown(self):
        self.db.stop()
        self.temp.cleanup()

    def test_asgi_startup_and_export_assets(self):
        with TestClient(app) as client:
            home = client.get('/')
            self.assertEqual(home.status_code, 200)
            self.assertIn('exportPreselection', home.text)
            module = client.get('/preselection.js')
            self.assertEqual(module.status_code, 200)
            self.assertIn('SunProPreselection', module.text)
            self.assertEqual(client.get('/api/leads').json(), [])
            self.assertEqual(client.get('/api/leads/missing').status_code, 404)
            self.assertEqual(client.get('/api/dossier/missing').status_code, 404)

    def test_streamlit_empty_database(self):
        page = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py'), default_timeout=30).run()
        self.assertEqual(list(page.exception), [])
        self.assertTrue(any('Nessun terreno nel database' in item.value for item in page.info))


if __name__ == '__main__':
    unittest.main()
