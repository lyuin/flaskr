import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import init_db


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update({
        'DATABASE': db_path,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    
    # Create the database and load test data
    with app.app_context():
        init_db()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self.client = client

    def login(self, username='admin', password='default'):
        return self.client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    """Helper fixture to log in and log out."""
    return AuthActions(client)
