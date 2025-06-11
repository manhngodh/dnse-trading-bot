from fastapi import APIRouter, HTTPException, status, Request, Response
from pydantic import BaseModel
from typing import Optional, List
import logging
from services.auth_service import AuthService
from services.session_manager import SessionManager

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

class AccountResponse(BaseModel):
    accountNo: str
    accountType: Optional[str] = None
    status: Optional[str] = None
    
class AccountsResponse(BaseModel):
    success: bool = True
    accounts: List[AccountResponse] = []

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    session_id: Optional[str] = None
    requires_otp: bool = False

@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, response: Response):
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
        
        # Set session cookie
        response.set_cookie(
            key="dnse_session_id",
            value=session_id,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        # Ensure session is initialized with otp_verified: False and trading_token: None
        session_manager = SessionManager()
        session_manager.update_session(session_id, {
            "otp_verified": False,
            "trading_token": None
        })
        
        # Don't request OTP automatically - let user browse data first
        # OTP will be requested when trading actions are attempted
        
        return {
            "access_token": auth_result["jwt_token"],
            "expires_in": 3600,  # Token typically expires in 1 hour
            "requires_otp": False,  # Changed: OTP not required immediately
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
async def verify_otp(otp_data: OTPRequest, response: Response):
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
        
        # Update session cookie to keep it fresh
        response.set_cookie(
            key="dnse_session_id",
            value=otp_data.session_id,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
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


@router.get("/accounts", response_model=AccountsResponse)
async def get_accounts(request: Request):
    """
    Get user's trading accounts
    """
    # Get session ID from cookie
    session_id = request.cookies.get("dnse_session_id")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session found. Please login first."
        )
    
    # Check if session exists in Redis
    session_manager = SessionManager()
    session_data = session_manager.get_session(session_id)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )
    
    # Create auth service with session ID to restore authenticated client
    auth_service = AuthService(session_id=session_id)
    
    try:
        # Get accounts from DNSE
        accounts = auth_service.get_accounts()
        
        # Format the accounts for the response model
        formatted_accounts = [
            {
                "accountNo": acc.get("accountNo", ""),
                "accountType": acc.get("accountType", "Standard"),
                "status": acc.get("status", "Active")
            }
            for acc in accounts
        ]
        
        # Extend session TTL
        session_manager.extend_session(session_id)
        
        return {
            "success": True,
            "accounts": formatted_accounts
        }
        
    except Exception as e:
        logger.error(f"Error fetching DNSE accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch DNSE accounts: {str(e)}"
        )

@router.get("/status")
async def get_status(request: Request):
    """
    Get current authentication and trading status for the user session
    """
    session_id = request.cookies.get("dnse_session_id")
    if not session_id:
        return {"authenticated": False, "has_trading_token": False}
    session_manager = SessionManager()
    session_data = session_manager.get_session(session_id)
    if not session_data:
        return {"authenticated": False, "has_trading_token": False}
    return {
        "authenticated": session_data.get("authenticated", False),
        "has_trading_token": bool(session_data.get("trading_token")),
        "trading_token": session_data.get("trading_token")
    }
