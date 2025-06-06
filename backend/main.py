from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

# Import core modules
from core.config import active_config
from core.logging import setup_logging

# Import route blueprints
from routes.auth import auth_bp
from routes.market import market_bp
from routes.order import order_bp
from routes.portfolio import portfolio_bp

# Initialize logging
logger = setup_logging()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure app from active configuration
    app.config.from_object(active_config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(market_bp, url_prefix='/api/market')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    
    # Basic health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    return app

# Entry point for WSGI servers
application = create_app()

if __name__ == '__main__':
    app = application
    
    print("🚀 Starting DNSE Trading Bot Backend Server...")
    print("🌐 Server running on http://localhost:5001")

    app.run(host='0.0.0.0', port=5001, debug=True)
