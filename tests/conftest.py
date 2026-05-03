import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-api-key')
    monkeypatch.setenv('GEMINI_MODEL', 'models/test-model')
    monkeypatch.setenv('GEMINI_API_ROOTS', 'https://example.invalid')

    database_path = tmp_path / 'test.db'
    app = create_app(
        {
            'TESTING': True,
            'DATABASE': str(database_path),
            'GEMINI_API_KEY': 'test-api-key',
            'GEMINI_MODEL': 'models/test-model',
            'GEMINI_API_ROOTS': ['https://example.invalid'],
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
