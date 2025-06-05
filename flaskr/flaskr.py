"""
Main module for the Flaskr application.
"""
import functools
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort,
    current_app
)

from .db import get_db

# Create a blueprint
bp = Blueprint('flaskr', __name__)


@bp.route('/')
def show_entries():
    """Show all entries in the database."""
    db = get_db()
    try:
        cur = db.execute('SELECT id, title, text FROM entries ORDER BY id DESC')
        entries = cur.fetchall()
    except Exception as e:
        flash(f'Error retrieving entries: {e}')
        entries = []
    return render_template('show_entries.html', entries=entries)


@bp.route('/add', methods=['POST'])
def add_entry():
    """Add a new entry to the database."""
    if not session.get('logged_in'):
        abort(401)
    
    title = request.form['title']
    text = request.form['text']
    
    # Simple form validation
    error = None
    if not title:
        error = 'Title is required.'
    elif not text:
        error = 'Text is required.'
    
    if error is not None:
        flash(error)
        return redirect(url_for('flaskr.show_entries'))
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO entries (title, text) VALUES (?, ?)',
            (title, text)
        )
        db.commit()
        flash('New entry was successfully posted')
    except Exception as e:
        db.rollback()
        flash(f'Error adding entry: {e}')
    
    return redirect(url_for('flaskr.show_entries'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple form validation
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif username != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif password != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session.clear()
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('flaskr.show_entries'))
    
    return render_template('login.html', error=error)


@bp.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete an entry from the database."""
    if not session.get('logged_in'):
        abort(401)
    
    db = get_db()
    try:
        db.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        db.commit()
        flash('Entry was successfully deleted')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting entry: {e}')
    
    return redirect(url_for('flaskr.show_entries'))


@bp.route('/logout')
def logout():
    """Log out a user."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('flaskr.show_entries'))


# For backwards compatibility
def init_db():
    """Initialize the database."""
    from .db import init_db as _init_db
    _init_db()
