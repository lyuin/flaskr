"""
Configuration module for the Flaskr application.
"""
import os
import secrets


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flaskr', 'flaskr.db')
    USERNAME = os.environ.get('FLASKR_USERNAME') or 'admin'
    PASSWORD = os.environ.get('FLASKR_PASSWORD') or 'default'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE = os.environ.get('TEST_DATABASE') or ':memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    # In production, these should be set in environment variables
    USERNAME = os.environ.get('FLASKR_USERNAME')
    PASSWORD = os.environ.get('FLASKR_PASSWORD')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}