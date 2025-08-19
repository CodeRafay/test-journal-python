from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, TEXT
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from models import Entry, EntryCreate, EntryUpdate

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
entries_collection = db.entries

async def init_database():
    """Initialize database with indexes"""
    try:
        # Create indexes for better performance
        indexes = [
            IndexModel([("title", TEXT), ("content", TEXT), ("tags", TEXT)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("isShared", ASCENDING)]),
            IndexModel([("dateCreated", ASCENDING)])
        ]
        await entries_collection.create_indexes(indexes)
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

async def create_entry(entry_data: EntryCreate) -> Entry:
    """Create a new journal entry"""
    entry_dict = entry_data.dict()
    entry_dict["_id"] = str(uuid.uuid4())
    entry_dict["dateCreated"] = datetime.utcnow()
    entry_dict["dateModified"] = datetime.utcnow()
    
    result = await entries_collection.insert_one(entry_dict)
    
    # Fetch the created entry
    created_entry = await entries_collection.find_one({"_id": result.inserted_id})
    return Entry(**created_entry)

async def get_entries(search: Optional[str] = None, category: Optional[str] = None, shared_only: bool = False) -> List[Entry]:
    """Get entries with optional search and filtering"""
    query = {}
    
    # Filter by visibility
    if shared_only:
        query["isShared"] = True
    
    # Filter by category
    if category and category != "all":
        query["category"] = category
    
    # Add search functionality
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [{"$regex": search, "$options": "i"}]}}
        ]
    
    # Fetch entries sorted by date created (newest first)
    cursor = entries_collection.find(query).sort("dateCreated", -1).limit(50)
    entries = await cursor.to_list(length=50)
    
    return [Entry(**entry) for entry in entries]

async def get_entry_by_id(entry_id: str) -> Optional[Entry]:
    """Get a single entry by ID"""
    entry = await entries_collection.find_one({"_id": entry_id})
    if entry:
        return Entry(**entry)
    return None

async def update_entry(entry_id: str, entry_update: EntryUpdate) -> Optional[Entry]:
    """Update an existing entry"""
    update_data = {k: v for k, v in entry_update.dict().items() if v is not None}
    
    if not update_data:
        return await get_entry_by_id(entry_id)
    
    update_data["dateModified"] = datetime.utcnow()
    
    result = await entries_collection.update_one(
        {"_id": entry_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        return None
    
    return await get_entry_by_id(entry_id)

async def delete_entry(entry_id: str) -> bool:
    """Delete an entry"""
    result = await entries_collection.delete_one({"_id": entry_id})
    return result.deleted_count > 0

async def get_categories(shared_only: bool = False) -> List[str]:
    """Get all unique categories"""
    query = {}
    if shared_only:
        query["isShared"] = True
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$category"}},
        {"$sort": {"_id": 1}}
    ]
    
    cursor = entries_collection.aggregate(pipeline)
    categories = [doc["_id"] async for doc in cursor if doc["_id"]]
    
    return categories

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
    client.close()