import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Pomodoro Timer' in response.data

def test_progress_get(client):
    response = client.get('/progress')
    assert response.status_code == 200
    data = response.get_json()
    assert 'sessionsCompleted' in data
    assert 'focusTime' in data

def test_progress_post(client):
    response = client.post('/progress', json={
        'sessionsCompleted': 2,
        'focusTime': 1500
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'saved'

    # Check if values are saved
    response = client.get('/progress')
    data = response.get_json()
    assert data['sessionsCompleted'] == 2
    assert data['focusTime'] == 1500
