"""
Database module for the Flaskr application.
"""
import sqlite3
from flask import current_app, g


def get_db():
    """Get a database connection.
    
    Returns:
        A database connection with row factory set to sqlite3.Row.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection.
    
    Args:
        e: An optional exception that occurred during the request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with the schema."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_app(app):
    """Register database functions with the Flask app.
    
    Args:
        app: The Flask application.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')