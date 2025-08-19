#!/usr/bin/env python3
"""
Quick deployment test script for separated architecture
Tests database connection and basic API functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.append(str(backend_path))

async def test_database_connection():
    """Test Vercel Postgres connection via Prisma"""
    try:
        from prisma import Prisma
        
        prisma = Prisma()
        await prisma.connect()
        
        # Test basic query
        count = await prisma.entry.count()
        print(f"✅ Database connected successfully (entries: {count})")
        
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_backend_startup():
    """Test if backend can start without errors"""
    try:
        # Import all modules to check for import errors
        from database import init_database, close_database
        from models import EntryCreate, EntryResponse
        from auth import authenticate_user
        from server import app
        
        print("✅ All backend modules imported successfully")
        
        # Test database initialization
        await init_database()
        await close_database()
        
        print("✅ Backend startup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    required_vars = [
        'DATABASE_URL',
        'ADMIN_PASSWORD', 
        'VIEWER_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

async def run_tests():
    """Run all deployment tests"""
    print("🧪 Running Deployment Tests")
    print("=" * 40)
    
    # Load environment variables
    env_file = backend_path / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("📁 Loaded environment from .env file")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Backend Startup", test_backend_startup),
        ("Database Connection", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
            print()
                
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)