import pytest
from flask import url_for
from playground.llm import ask_llm
from playground.tools import register_tool

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

def test_chat_completions(client):
    history = []
    result = ask_llm(history, 'Respond with: Hello World')
    assert "Hello World" in result

def test_tool_calling(client):
    history = []

    def hello_tool(*args, **kwargs):
        return "hello from tool"

    register_tool(hello_tool)
    result = ask_llm(history, 'use the hello world tool', use_tools=True)
    assert "hello from tool" in result
    