from flask import Blueprint, request, jsonify
from ..services.portfolio_service import PortfolioService
from ..exceptions import DNSEAPIError

portfolio_bp = Blueprint('portfolio', __name__)
portfolio_service = PortfolioService()

@portfolio_bp.route('/<account_no>', methods=['GET'])
def get_portfolio(account_no):
    try:
        result = portfolio_service.get_portfolio(account_no)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@portfolio_bp.route('/buying-power/<account_no>', methods=['GET']) 
def get_buying_power(account_no):
    try:
        result = portfolio_service.get_buying_power(account_no)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
        
# UI DNSE portfolio endpoints
@portfolio_bp.route('/ui', methods=['GET'])
def get_portfolio_ui():
    try:
        account_index = request.args.get('account_index', type=int) 
        result = portfolio_service.get_portfolio_ui(account_index)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while loading portfolio'
        }), 500

# Demo portfolio endpoints
@portfolio_bp.route('/demo/<account_no>', methods=['GET'])
def get_demo_portfolio(account_no):
    try:
        result = portfolio_service.get_demo_portfolio(account_no)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@portfolio_bp.route('/demo/reset/<account_no>', methods=['POST'])
def reset_demo_portfolio(account_no):
    try:
        result = portfolio_service.reset_demo_portfolio(account_no)
        return jsonify({
            'success': True,
            'message': f'Portfolio reset for account {account_no}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500
