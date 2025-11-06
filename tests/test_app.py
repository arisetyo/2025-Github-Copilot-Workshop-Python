import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app

@pytest.fixture
def client():
    """
    Setup Flask test client
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """
    Test the index route returns 200 and contains expected content
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Pomodoro Timer' in response.data

def test_progress_get_default(client):
    response = client.get('/progress')
    assert response.status_code == 200
    data = response.get_json()
    assert data['sessionsCompleted'] == 0
    assert data['focusTime'] == 0

def test_progress_post_and_get(client):
    # Post valid progress
    post_data = {'sessionsCompleted': 3, 'focusTime': 1500}
    response = client.post('/progress', json=post_data)
    assert response.status_code == 200
    assert response.get_json()['status'] == 'saved'

    # Get progress and check values
    response = client.get('/progress')
    data = response.get_json()
    assert data['sessionsCompleted'] == 3
    assert data['focusTime'] == 1500

def test_progress_post_invalid_data(client):
    # Post invalid progress (non-int values)
    post_data = {'sessionsCompleted': 'three', 'focusTime': 'fifteen'}
    response = client.post('/progress', json=post_data)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_settings_ui_present(client):
    """
    Test that the settings UI elements are present in the page
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Settings' in response.data
    assert b'work-duration' in response.data
    assert b'break-duration' in response.data
    assert b'theme-selector' in response.data
    assert b'sound-enabled' in response.data

def test_work_duration_options(client):
    """
    Test that work duration dropdown has all required options
    """
    response = client.get('/')
    assert b'15 min' in response.data
    assert b'25 min' in response.data
    assert b'35 min' in response.data
    assert b'45 min' in response.data

def test_break_duration_options(client):
    """
    Test that break duration dropdown has all required options
    """
    response = client.get('/')
    assert b'5 min' in response.data or b'5</option>' in response.data
    assert b'10 min' in response.data or b'10</option>' in response.data
    assert b'15 min' in response.data or b'15</option>' in response.data

def test_theme_options(client):
    """
    Test that theme selector has all required options
    """
    response = client.get('/')
    assert b'Light' in response.data
    assert b'Dark' in response.data
    assert b'Focus' in response.data
