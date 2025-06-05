"""
Flaskr application package.
"""
import os
from flask import Flask
from .config import config


def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: The name of the configuration to use. Defaults to the
            FLASK_ENV environment variable or 'default'.
    
    Returns:
        The configured Flask application.
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Register database functions
    from . import db
    db.init_app(app)
    
    # Register routes
    from . import flaskr
    app.register_blueprint(flaskr.bp)
    
    return app

# For backwards compatibility
from .flaskr import init_db, get_db
app = create_app()
