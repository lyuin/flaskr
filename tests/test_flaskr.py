import pytest
import sqlite3
from flask import g
from flaskr.db import get_db


def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Amazon Q Developer Python Flask Demo' in response.data


def test_get_db(app):
    """Test that get_db returns the same connection each time it's called."""
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_init_db_command(runner, monkeypatch):
    """Test the init-db command."""
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_db_connection(app):
    """Test that the database connection works."""
    with app.app_context():
        db = get_db()
        assert isinstance(db, sqlite3.Connection)


def test_close_db(app):
    """Test that close_db closes the database connection."""
    with app.app_context():
        db = get_db()
        assert db is get_db()
        
    # Outside of app context, db should be closed


def test_login(client, auth):
    """Test login functionality."""
    # Test GET request to login page
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    
    # Test successful login
    response = auth.login()
    assert response.status_code == 200
    assert b'You were logged in' in response.data
    assert b'log out' in response.data
    
    # Test logout
    response = auth.logout()
    assert b'You were logged out' in response.data
    assert b'log in' in response.data


def test_login_validation(client):
    """Test login validation."""
    # Test invalid username
    response = client.post('/login', data={
        'username': 'invalid',
        'password': 'default'
    }, follow_redirects=True)
    assert b'Invalid username' in response.data
    
    # Test invalid password
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'invalid'
    }, follow_redirects=True)
    assert b'Invalid password' in response.data


def test_add_entry(client, auth, app):
    """Test adding an entry."""
    # Login first
    auth.login()
    
    # Add an entry
    response = client.post('/add', data={
        'title': 'Test Title',
        'text': 'Test Content'
    }, follow_redirects=True)
    assert b'New entry was successfully posted' in response.data
    assert b'Test Title' in response.data
    assert b'Test Content' in response.data
    
    # Verify entry was added to database
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM entries').fetchone()[0]
        assert count > 0


def test_delete_entry(client, auth, app):
    """Test deleting an entry."""
    # Login first
    auth.login()
    
    # Add an entry
    client.post('/add', data={
        'title': 'Delete Test',
        'text': 'This entry will be deleted'
    })
    
    # Get the entry ID
    with app.app_context():
        db = get_db()
        entry = db.execute('SELECT id FROM entries WHERE title = ?', 
                          ('Delete Test',)).fetchone()
        
    if entry:
        # Delete the entry
        response = client.post(f'/delete/{entry["id"]}', follow_redirects=True)
        assert b'Entry was successfully deleted' in response.data
        
        # Verify entry was deleted from database
        with app.app_context():
            db = get_db()
            entry = db.execute('SELECT * FROM entries WHERE title = ?', 
                              ('Delete Test',)).fetchone()
            assert entry is None


def test_unauthorized_access(client):
    """Test unauthorized access to protected routes."""
    # Try to add an entry without logging in
    response = client.post('/add', data={
        'title': 'Unauthorized',
        'text': 'This should not be added'
    })
    assert response.status_code == 401
    
    # Try to delete an entry without logging in
    response = client.post('/delete/1')
    assert response.status_code == 401

