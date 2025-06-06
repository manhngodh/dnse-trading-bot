from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from exceptions import DNSEAPIError

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        result = auth_service.authenticate(username, password)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        otp_code = data.get('otp')
        
        result = auth_service.verify_otp(otp_code)
        return jsonify(result)
    except DNSEAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
