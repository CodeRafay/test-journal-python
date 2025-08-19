from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Import local modules
from models import *
from auth import *
from database import *

# Load environment variables
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()

# Create the main app
app = FastAPI(lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Journal API is running with Prisma + PostgreSQL"}

# Authentication endpoints
@api_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """Authenticate user with password"""
    try:
        role = authenticate_user(request.password)
        
        if not role:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        set_session_cookie(response, role)
        
        return LoginResponse(
            role=role,
            message=f"Successfully logged in as {role}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.post("/logout", response_model=APIResponse)
async def logout(response: Response):
    """Logout user and clear session"""
    clear_session_cookie(response)
    return APIResponse(message="Successfully logged out")

# Entry management endpoints
@api_router.get("/entries")
async def get_entries_endpoint(
    request: Request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    grouped: bool = True
):
    """Get entries with optional search and category filtering"""
    try:
        role = require_auth(request)
        shared_only = role == "viewer"
        
        if grouped:
            entries_grouped = await get_entries_grouped_by_category(
                search=search, 
                shared_only=shared_only
            )
            return {"grouped": entries_grouped}
        else:
            entries = await get_entries(
                search=search, 
                category=category, 
                shared_only=shared_only
            )
            return {"entries": entries}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get entries error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch entries")

@api_router.post("/entries", response_model=EntryResponse)
async def create_entry_endpoint(request: Request, entry_data: EntryCreate):
    """Create a new journal entry (admin only)"""
    try:
        require_admin(request)
        entry = await create_entry(entry_data)
        return entry
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create entry error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create entry")

@api_router.put("/entries/{entry_id}", response_model=EntryResponse)
async def update_entry_endpoint(request: Request, entry_id: str, entry_update: EntryUpdate):
    """Update an existing entry (admin only)"""
    try:
        require_admin(request)
        
        updated_entry = await update_entry(entry_id, entry_update)
        
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return updated_entry
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update entry error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update entry")

@api_router.delete("/entries/{entry_id}", response_model=APIResponse)
async def delete_entry_endpoint(request: Request, entry_id: str):
    """Delete an entry (admin only)"""
    try:
        require_admin(request)
        
        deleted = await delete_entry(entry_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return APIResponse(message="Entry deleted successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete entry error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete entry")

# Category management endpoints
@api_router.get("/categories")
async def get_categories_endpoint(request: Request):
    """Get all categories"""
    try:
        role = require_auth(request)
        shared_only = role == "viewer"
        
        categories = await get_categories(shared_only=shared_only)
        return {"categories": categories}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

# Include the router in the main app
app.include_router(api_router)