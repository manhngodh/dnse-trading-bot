from flask import Blueprint, request, jsonify
from ..services.market_service import MarketService
from ..exceptions import DNSEAPIError

market_bp = Blueprint('market', __name__)
market_service = MarketService()

@market_bp.route('/stock-info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    try:
        result = market_service.get_stock_info(symbol)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@market_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    try:
        result = market_service.get_market_data(symbol)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
