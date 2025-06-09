from dnse_client import DNSEClient
from exceptions import DNSEAPIError
from typing import Dict, Any, Optional
import logging

# Create module logger
logger = logging.getLogger("dnse-trading.auth_service")

# Dictionary to store active sessions by session_id
active_sessions = {}

class AuthService:
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the auth service. If a session_id is provided, 
        try to load the existing client from active sessions.
        
        Args:
            session_id: Optional session ID to restore an existing session
        """
        if session_id and session_id in active_sessions:
            self.client = active_sessions[session_id]
            logger.info(f"Restored session for session_id: {session_id}")
        else:
            self.client = DNSEClient()
            logger.info("New DNSE client created")
    
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with DNSE platform
        
        Args:
            username: DNSE username
            password: DNSE password
            
        Returns:
            Dictionary with jwt_token and investor_info
            
        Raises:
            DNSEAPIError: If authentication fails
        """
        try:
            logger.info(f"Authenticating user: {username}")
            self.client.username = username
            self.client.password = password
            success = self.client.authenticate()
            
            if success:
                # Get investor information
                investor_info = self.client.get_investor_info()
                
                # Create session ID from account number
                session_id = str(investor_info.get("accountNumber", ""))
                
                # Store client in active sessions
                active_sessions[session_id] = self.client
                logger.info(f"Authentication successful, created session: {session_id}")
                
                return {
                    'jwt_token': self.client.jwt_token,
                    'investor_info': investor_info
                }
            else:
                raise DNSEAPIError("Authentication failed")
        except DNSEAPIError as e:
            logger.error(f"DNSE authentication error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise DNSEAPIError(f"Authentication error: {str(e)}")

    def verify_otp(self, otp_code: str, session_id: Optional[str] = None) -> Dict[str, str]:
        """
        Verify OTP and get trading token
        
        Args:
            otp_code: The OTP code received via email
            session_id: Optional session ID to use a specific client
            
        Returns:
            Dictionary with trading_token
            
        Raises:
            DNSEAPIError: If OTP verification fails or no JWT token available
        """
        # If session_id provided, try to use that client
        if session_id and session_id in active_sessions:
            self.client = active_sessions[session_id]
            logger.info(f"Using client from session: {session_id}")
        
        if not self.client.jwt_token:
            logger.error("No JWT token available, authentication required before OTP verification")
            raise DNSEAPIError("Must authenticate first before verifying OTP")
            
        try:
            logger.info(f"Verifying OTP for session: {session_id}")
            trading_token = self.client.verify_otp_email(otp_code)
            
            # Update client in active sessions with trading token
            if session_id:
                active_sessions[session_id] = self.client
            
            logger.info(f"OTP verification successful for session: {session_id}")
            return {'trading_token': trading_token}
        except DNSEAPIError as e:
            logger.error(f"OTP verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification: {str(e)}")
            raise DNSEAPIError(f"OTP verification error: {str(e)}")
            
    def request_otp(self, session_id: Optional[str] = None) -> bool:
        """
        Request OTP via email
        
        Args:
            session_id: Optional session ID to use a specific client
            
        Returns:
            True if request was successful
            
        Raises:
            DNSEAPIError: If OTP request fails
        """
        # If session_id provided, try to use that client
        if session_id and session_id in active_sessions:
            self.client = active_sessions[session_id]
            logger.info(f"Using client from session: {session_id}")
        
        if not self.client.jwt_token:
            logger.error("No JWT token available, authentication required before OTP request")
            raise DNSEAPIError("Must authenticate first before requesting OTP")
            
        try:
            logger.info(f"Requesting OTP email for session: {session_id}")
            success = self.client.request_otp_email()
            
            if success:
                logger.info(f"OTP email request successful for session: {session_id}")
                return True
            else:
                logger.error("OTP request failed without exception")
                raise DNSEAPIError("Failed to request OTP")
        except DNSEAPIError as e:
            logger.error(f"OTP request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during OTP request: {str(e)}")
            raise DNSEAPIError(f"OTP request error: {str(e)}")
