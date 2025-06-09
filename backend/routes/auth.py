from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging
from services.auth_service import AuthService

# Create module logger
logger = logging.getLogger("dnse-trading")

router = APIRouter()

# Define request and response models
class LoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    otp_code: str
    session_id: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    session_id: Optional[str] = None
    requires_otp: bool = False

@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user with DNSE Trading API
    """
    auth_service = AuthService()
    
    try:
        # Log login attempt to DNSE platform
        logger.info(f"DNSE login attempt for user: {login_data.username}")
        
        # Authenticate with DNSE
        auth_result = auth_service.authenticate(
            username=login_data.username,
            password=login_data.password
        )
        
        # Authentication successful
        logger.info(f"DNSE login successful for user: {login_data.username}")
        
        # Get session ID from investor info
        session_id = str(auth_result["investor_info"]["investorId"])
        
        # Request OTP for trading
        auth_service.request_otp(session_id)
        
        return {
            "access_token": auth_result["jwt_token"],
            "expires_in": 3600,  # Token typically expires in 1 hour
            "requires_otp": True,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"DNSE login error for user: {login_data.username} - {str(e)}")
        
        # Return appropriate error based on exception type
        if "401" in str(e) or "Unauthorized" in str(e) or "Invalid credentials" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid DNSE credentials"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DNSE authentication error: {str(e)}"
            )

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(otp_data: OTPRequest):
    """
    Verify OTP code for second-factor authentication with DNSE
    """
    logger.info(f"DNSE OTP verification attempt for session: {otp_data.session_id}")
    
    # Create a new auth service with the existing session ID
    auth_service = AuthService(session_id=otp_data.session_id)
    
    try:
        # Verify OTP with DNSE
        result = auth_service.verify_otp(
            otp_code=otp_data.otp_code,
            session_id=otp_data.session_id
        )
        
        # OTP verification successful
        logger.info(f"DNSE OTP verification successful for session: {otp_data.session_id}")
        
        return {
            "access_token": result["trading_token"],  # Access the trading token directly
            "expires_in": 3600,  # Token typically expires in 1 hour
            "requires_otp": False
        }
    except Exception as e:
        logger.error(f"DNSE OTP verification failed for session: {otp_data.session_id} - {str(e)}")
        
        if "invalid" in str(e).lower() or "expired" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP code"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DNSE OTP verification error: {str(e)}"
            )
