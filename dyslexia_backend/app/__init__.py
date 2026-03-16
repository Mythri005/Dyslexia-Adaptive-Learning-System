from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # FIX CORS - Allow all origins during development
    CORS(app)
    
    # Or for development, you can allow all origins:
    # CORS(app)  # This allows all origins (use only for development)
    
    # Create tables
    with app.app_context():
        from app.models.user import User
        from app.models.progress import Progress
        from app.models.session import LearningSession
        db.create_all()
    
    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.math_routes import math_bp
    from app.routes.spelling_routes import spelling_bp
    from app.routes.reading_routes import reading_bp
    from app.routes.camera_routes import camera_bp
    from app.routes.monitoring_routes import monitoring_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(math_bp, url_prefix='/api/math')
    app.register_blueprint(spelling_bp, url_prefix='/api/spelling')
    app.register_blueprint(reading_bp, url_prefix='/api/reading')
    app.register_blueprint(camera_bp, url_prefix='/api/camera')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    
    return app
