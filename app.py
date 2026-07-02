"""
Main Flask application for OPTC Farming Bot web interface
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///farmbot.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'memory://'))
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'cache+memory://')
    app.config['CELERY_TASK_ALWAYS_EAGER'] = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'
    
    if test_config:
        app.config.update(test_config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": os.getenv('ALLOWED_ORIGINS', '*')}})
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    from tasks import configure_celery
    configure_celery(app)
    
    # Register blueprints
    from api.routes import api_bp
    from web.routes import web_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp, url_prefix='/')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info('Database tables created')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f'Server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info('Flask app created successfully')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', False)
    )
