from flask import Flask
from flask_cors import CORS
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app():
    """Construct the core application."""
    blueprint = make_twitter_blueprint(
        api_key="ZYSzeoldYmoDO0N3D4wo0hm8z",
        api_secret="EP90Ut2kgSLyE6bI9IutCyLS0rF3jYB95s4gMXa59kBBo64Mld",
    )
    app = Flask(__name__, instance_relative_config=False)
    CORS(app)
    app.config.from_object('config.Config')
    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        db.create_all()  # Create sql tables for our data models
        app.register_blueprint(blueprint, url_prefix="/login")
        return app
