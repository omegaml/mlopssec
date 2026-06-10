import pytest
from flask import url_for

# If you have a create_app factory, import and use it:
# from myapp import create_app

@pytest.fixture
def client():
    # replace with create_app() if you use a factory
    from playground.app import app
    app.config.update({'TESTING': True})
    with app.test_client() as client:
        yield client

def test_login_redirect(client):
    # adjust the protected path to match your app
    resp = client.get('/', follow_redirects=False)
    # Flask-Login typically responds with 302 redirect to login view
    assert resp.status_code in (302, 303), "this is not secure yet (add required login)"
    # redirect Location should point to login (may include next param)
    location = resp.headers.get('Location', '')
    assert '/login' in location or 'login' in location.lower()