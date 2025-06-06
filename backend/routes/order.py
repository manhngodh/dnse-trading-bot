from flask import Blueprint, request, jsonify
from ..services.order_service import OrderService
from ..exceptions import DNSEAPIError

order_bp = Blueprint('order', __name__)
order_service = OrderService()

@order_bp.route('/orders', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        result = order_service.place_order(data)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/orders/<order_id>', methods=['GET'])
def get_order_details(order_id):
    try:
        account_no = request.args.get('accountNo')
        result = order_service.get_order_details(order_id, account_no)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/orders/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    try:
        account_no = request.args.get('accountNo')
        result = order_service.cancel_order(order_id, account_no)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/orders/pending', methods=['GET'])
def get_pending_orders():
    try:
        account_no = request.args.get('accountNo')
        result = order_service.get_pending_orders(account_no)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
