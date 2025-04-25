from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app."""
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all() 