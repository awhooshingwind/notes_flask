import pytest
from flask import g, session
from noter.db import get_db 

def test_register(client, app):
    assert client.get('auth/register').status_code == 200
    response = client.post(
        'auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/index"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None
    
@pytest.mark.parametrize(('username', 'password', 'message'),( ('', '', b'We need to call you something...pick a username'),
('a', '', b'You need a password to get back in'),
('test', 'test', b'already exists'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        'auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/index"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Nobody called that around here...'),
    ('test', 'a', b'Wrong password'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session