import os
import tempfile

import pytest
from app import create_app
from app.db import init_db


@pytest.fixture

def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app = create_app()
    app.config.update({'TESTING': True, 'DATABASE': db_path})

    with app.app_context():
        init_db(app)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture

def client(app):
    return app.test_client()


def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200
    # Check for key elements in the new design
    response_text = response.get_data(as_text=True)
    assert 'Flashcard' in response_text or 'Kart' in response_text


def test_index_post_creates_results(client):
    response = client.post('/', data={'note_text': 'AI is a field of study.'})
    assert response.status_code == 200
    assert b'Flashcard' in response.data or b'Olu' in response.data


def test_card_lifecycle(client):
    response = client.post('/', data={'note_text': 'Python is a programming language.'})
    assert response.status_code == 200
    response = client.post('/save-card', data={'question': 'Test?', 'answer': 'Answer.', 'source': 'Python'})
    assert response.status_code == 302
    response = client.get('/cards')
    assert b'Python' in response.data
