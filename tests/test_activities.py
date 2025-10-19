from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import app

client = TestClient(app.app)


def test_get_activities():
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    # Expect known activities present
    assert 'Chess Club' in data


def test_signup_and_remove_participant():
    activity = 'Chess Club'
    email = 'pytest_user@example.com'

    # Ensure not present
    activities = client.get('/activities').json()
    if email in activities[activity]['participants']:
        # remove if exists
        r = client.delete(f"/activities/{activity}/participants", params={'email': email})
        assert r.status_code in (200, 404)

    # Signup
    r = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert r.status_code == 200
    assert 'Signed up' in r.json().get('message', '')

    # Confirm added
    activities = client.get('/activities').json()
    assert email in activities[activity]['participants']

    # Remove
    r2 = client.delete(f"/activities/{activity}/participants", params={'email': email})
    assert r2.status_code == 200
    assert 'Unregistered' in r2.json().get('message', '')

    # Confirm removed
    activities = client.get('/activities').json()
    assert email not in activities[activity]['participants']


def test_signup_nonexistent_activity():
    r = client.post('/activities/NoSuchActivity/signup', params={'email': 'a@b.c'})
    assert r.status_code == 404


def test_remove_nonexistent_participant():
    activity = 'Chess Club'
    email = 'definitely_not_present@example.com'
    r = client.delete(f"/activities/{activity}/participants", params={'email': email})
    assert r.status_code == 404
