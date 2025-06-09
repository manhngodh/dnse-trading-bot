from flask import Blueprint, request, jsonify
from services.order_service import OrderService
from exceptions import DNSEAPIError

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

@order_bp.route('/orders/history', methods=['GET'])
def get_order_history():
    try:
        account_no = request.args.get('accountNo')
        symbol = request.args.get('symbol')
        status = request.args.get('status')
        
        # Create a filters dictionary with only non-None values
        filters = {}
        if symbol:
            filters['symbol'] = symbol
        if status:
            filters['status'] = status
            
        # Get all orders using the standard orders endpoint and filter them
        result = order_service.get_orders(account_no)
        
        # Apply any additional filtering on the client side if needed
        if filters:
            filtered_orders = []
            for order in result:
                include = True
                if 'symbol' in filters and filters['symbol'] != order.get('symbol'):
                    include = False
                if 'status' in filters and filters['status'] != order.get('orderStatus'):
                    include = False
                if include:
                    filtered_orders.append(order)
            result = filtered_orders
            
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
