from ..interfaces.trading_client import ITradingClient
from ..dnse_client import DNSEClient

class AuthService:
    def __init__(self):
        self.client = DNSEClient()
    
    def authenticate(self, username: str, password: str) -> dict:
        """
        Authenticate user with DNSE platform
        """
        self.client.username = username
        self.client.password = password
        success = self.client.authenticate()
        
        if success:
            return {
                'jwt_token': self.client.jwt_token,
                'investor_info': self.client.get_investor_info()
            }
        else:
            raise Exception("Authentication failed")

    def verify_otp(self, otp_code: str) -> dict:
        """
        Verify OTP and get trading token
        """
        if not self.client.jwt_token:
            raise Exception("Must authenticate first")
            
        trading_token = self.client.verify_otp_email(otp_code)
        return {'trading_token': trading_token}
