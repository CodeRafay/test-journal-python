import os
import bcrypt
from fastapi import HTTPException, Request, Response
from typing import Optional

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(password: str) -> Optional[str]:
    """Authenticate user and return role if valid"""
    admin_hash = os.environ.get('ADMIN_PASSWORD')
    viewer_hash = os.environ.get('VIEWER_PASSWORD')
    
    if not admin_hash or not viewer_hash:
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if verify_password(password, admin_hash):
        return "admin"
    elif verify_password(password, viewer_hash):
        return "viewer"
    
    return None

def set_session_cookie(response: Response, role: str) -> None:
    """Set secure session cookie"""
    response.set_cookie(
        key="session",
        value=f"role={role}",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )

def get_current_user(request: Request) -> Optional[str]:
    """Get current user role from session cookie"""
    session = request.cookies.get("session")
    if not session:
        return None
    
    try:
        # Parse session cookie (format: "role=admin" or "role=viewer")
        if session.startswith("role="):
            role = session.split("=", 1)[1]
            if role in ["admin", "viewer"]:
                return role
    except:
        pass
    
    return None

def require_auth(request: Request) -> str:
    """Require authentication and return user role"""
    role = get_current_user(request)
    if not role:
        raise HTTPException(status_code=401, detail="Authentication required")
    return role

def require_admin(request: Request) -> str:
    """Require admin authentication"""
    role = require_auth(request)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return role

def clear_session_cookie(response: Response) -> None:
    """Clear session cookie"""
    response.delete_cookie(key="session")