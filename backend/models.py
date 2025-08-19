from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"

class EntryBase(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str] = []
    isShared: bool = False

class EntryCreate(EntryBase):
    pass

class EntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    isShared: Optional[bool] = None

class Entry(EntryBase):
    id: str = Field(alias="_id")
    dateCreated: datetime
    dateModified: datetime
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    role: str
    message: str

class CategoryCreate(BaseModel):
    name: str

class APIResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    statusCode: int