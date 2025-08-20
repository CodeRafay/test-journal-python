from prisma import Prisma
from prisma.models import Entry
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from models import EntryCreate, EntryUpdate
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Prisma client instance
prisma = Prisma()

async def init_database():
    """Initialize database connection and ensure schema is deployed"""
    try:
        await prisma.connect()
        print("Connected to PostgreSQL database via Prisma")
    except Exception as e:
        print(f"Database connection error: {e}")

async def create_entry(entry_data: EntryCreate) -> Entry:
    """Create a new journal entry"""
    # Convert tags array to comma-separated string for SQLite
    tags_str = ",".join(entry_data.tags) if entry_data.tags else ""
    
    entry = await prisma.entry.create(
        data={
            'title': entry_data.title,
            'content': entry_data.content,
            'category': entry_data.category,
            'tags': tags_str,
            'isShared': entry_data.isShared,
        }
    )
    
    # Convert tags back to array for response
    entry.tags = entry.tags.split(",") if entry.tags else []
    return entry

async def get_entries(search: Optional[str] = None, category: Optional[str] = None, shared_only: bool = False) -> List[Entry]:
    """Get entries with optional search and filtering"""
    where_conditions = {}
    
    # Filter by visibility
    if shared_only:
        where_conditions['isShared'] = True
    
    # Filter by category
    if category and category != "all":
        where_conditions['category'] = category
    
    # Add search functionality (SQLite text search)
    if search:
        where_conditions['OR'] = [
            {'title': {'contains': search}},
            {'content': {'contains': search}},
            {'tags': {'contains': search}},  # Search in comma-separated tags
        ]
    
    # Fetch entries sorted by date created (newest first)
    entries = await prisma.entry.find_many(
        where=where_conditions,
        take=50
    )
    
    # Sort in Python since Prisma syntax is having issues
    entries = sorted(entries, key=lambda x: x.dateCreated, reverse=True)
    
    # Convert tags from string to array for all entries
    for entry in entries:
        entry.tags = entry.tags.split(",") if entry.tags else []
    
    return entries

async def get_entry_by_id(entry_id: str) -> Optional[Entry]:
    """Get a single entry by ID"""
    entry = await prisma.entry.find_unique(
        where={'id': entry_id}
    )
    if entry:
        # Convert tags from string to array
        entry.tags = entry.tags.split(",") if entry.tags else []
    return entry

async def update_entry(entry_id: str, entry_update: EntryUpdate) -> Optional[Entry]:
    """Update an existing entry"""
    update_data = {k: v for k, v in entry_update.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        return await get_entry_by_id(entry_id)
    
    try:
        updated_entry = await prisma.entry.update(
            where={'id': entry_id},
            data=update_data
        )
        return updated_entry
    except Exception:
        # Entry not found
        return None

async def delete_entry(entry_id: str) -> bool:
    """Delete an entry"""
    try:
        await prisma.entry.delete(
            where={'id': entry_id}
        )
        return True
    except Exception:
        # Entry not found
        return False

async def get_categories(shared_only: bool = False) -> List[str]:
    """Get all unique categories"""
    where_condition = {}
    if shared_only:
        where_condition['isShared'] = True
    
    # Get unique categories using Prisma's distinct
    entries = await prisma.entry.find_many(
        where=where_condition
    )
    
    categories = list(set([entry.category for entry in entries if entry.category]))
    return sorted(categories)

async def get_entries_grouped_by_category(search: Optional[str] = None, shared_only: bool = False) -> Dict[str, List[Entry]]:
    """Get entries grouped by category"""
    entries = await get_entries(search=search, shared_only=shared_only)
    
    grouped = {}
    for entry in entries:
        category = entry.category or "Uncategorized"
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(entry)
    
    return grouped

async def close_database():
    """Close database connection"""
    await prisma.disconnect()