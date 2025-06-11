from dnse_client import DNSEClient
from exceptions import DNSEAPIError
from services.session_manager import SessionManager
from typing import Dict, Any, Optional, List
import logging

# Create module logger
logger = logging.getLogger("dnse-trading.auth_service")

class AuthService:
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the auth service with Redis session management.
        
        Args:
            session_id: Optional session ID to restore an existing session
        """
        self.session_manager = SessionManager()
        self.session_id = session_id
        
        if session_id:
            # Try to restore client from Redis session
            self.client = self._restore_client_from_session(session_id)
            logger.info(f"Restored session for session_id: {session_id}")
        else:
            self.client = DNSEClient()
            logger.info("New DNSE client created")
    
    def _restore_client_from_session(self, session_id: str) -> DNSEClient:
        """
        Restore DNSE client from Redis session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Restored DNSEClient instance
            
        Raises:
            DNSEAPIError: If session not found or restoration fails
        """
        try:
            session_data = self.session_manager.get_session(session_id)
            if not session_data:
                logger.error(f"No session found for ID: {session_id}")
                raise DNSEAPIError("Session not found or expired")
            
            # Create client with credentials
            client = DNSEClient(
                username=session_data.get("username"),
                password=session_data.get("password")
            )
            
            # Restore tokens and data
            client.jwt_token = session_data.get("jwt_token")
            client.trading_token = session_data.get("trading_token")
            client.investor_info = session_data.get("investor_info")
            client.accounts = session_data.get("accounts")
            client.loan_packages = session_data.get("loan_packages")
            
            logger.info(f"Client restored from session: {session_id}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to restore client from session {session_id}: {e}")
            raise DNSEAPIError(f"Failed to restore session: {str(e)}")
    
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with DNSE platform and create Redis session
        
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
            
            # Create new client
            self.client = DNSEClient(username=username, password=password)
            success = self.client.authenticate()
            
            if success:
                # Get investor information
                investor_info = self.client.get_investor_info()
                
                # Create session ID from investor ID
                self.session_id = str(investor_info.get("investorId", ""))
                
                # Store session in Redis
                session_data = {
                    "username": username,
                    "password": password,  # Note: Consider encrypting this in production
                    "jwt_token": self.client.jwt_token,
                    "trading_token": self.client.trading_token,
                    "investor_info": investor_info,
                    "accounts": None,  # Will be populated later
                    "loan_packages": None,
                    "authenticated": True,
                    "otp_verified": False
                }
                
                self.session_manager.create_session(self.session_id, session_data)
                logger.info(f"Authentication successful, created session: {self.session_id}")
                
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

    def verify_otp(self, otp_code: str, session_id: str) -> Dict[str, str]:
        """
        Verify OTP and get trading token
        
        Args:
            otp_code: The OTP code received via email
            session_id: Session ID to verify OTP for
            
        Returns:
            Dictionary with trading_token
            
        Raises:
            DNSEAPIError: If OTP verification fails or no JWT token available
        """
        try:
            if not self.client or not self.client.jwt_token:
                logger.error("No JWT token available, authentication required before OTP verification")
                raise DNSEAPIError("Must authenticate first before verifying OTP")
            
            logger.info(f"Verifying OTP for session: {session_id}")
            trading_token = self.client.verify_otp_email(otp_code)
            
            # Update session with trading token
            self.session_manager.update_session(session_id, {
                "trading_token": trading_token,
                "otp_verified": True
            })
            
            logger.info(f"OTP verification successful for session: {session_id}")
            
            return {
                'trading_token': trading_token
            }
            
        except DNSEAPIError as e:
            logger.error(f"OTP verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification: {str(e)}")
            raise DNSEAPIError(f"OTP verification error: {str(e)}")
            
    def request_otp(self, session_id: str) -> bool:
        """
        Request OTP via email
        
        Args:
            session_id: Session ID to request OTP for
            
        Returns:
            True if request was successful
            
        Raises:
            DNSEAPIError: If OTP request fails
        """
        try:
            if not self.client or not self.client.jwt_token:
                logger.error("No JWT token available, authentication required before OTP request")
                raise DNSEAPIError("Must authenticate first before requesting OTP")
            
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
            
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get user's trading accounts and cache in session
        
        Returns:
            List of account dictionaries
            
        Raises:
            DNSEAPIError: If account retrieval fails
        """
        try:
            if not self.client or not self.client.jwt_token:
                logger.error("No JWT token available, authentication required before fetching accounts")
                raise DNSEAPIError("Must authenticate first before getting accounts")
            
            logger.info("Fetching user accounts")
            accounts = self.client.get_accounts()
            
            # Update session with accounts data
            if self.session_id:
                self.session_manager.update_session(self.session_id, {
                    "accounts": accounts
                })
            
            if accounts:
                logger.info(f"Successfully fetched {len(accounts)} accounts")
                return accounts
            else:
                logger.warning("No accounts found")
                return []
                
        except DNSEAPIError as e:
            logger.error(f"Failed to fetch accounts: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching accounts: {str(e)}")
            raise DNSEAPIError(f"Failed to fetch accounts: {str(e)}")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session information
        """
        return self.session_manager.get_session_info(session_id)
    
    def logout(self, session_id: str) -> bool:
        """
        Logout and delete session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if logout successful
        """
        try:
            success = self.session_manager.delete_session(session_id)
            if success:
                logger.info(f"User logged out, session deleted: {session_id}")
            return success
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False
