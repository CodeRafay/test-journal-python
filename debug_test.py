#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/app/backend')

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://username:password@localhost:5432/journal_db'

async def debug_imports():
    print("Testing imports step by step...")
    
    try:
        print("1. Importing Prisma...")
        from prisma import Prisma
        print("✅ Prisma imported")
        
        print("2. Importing Entry model...")
        from prisma.models import Entry
        print("✅ Entry model imported")
        
        print("3. Creating Prisma client...")
        prisma = Prisma()
        print("✅ Prisma client created")
        
        print("4. Connecting to database...")
        await prisma.connect()
        print("✅ Database connected")
        
        print("5. Testing find_many directly...")
        entries = await prisma.entry.find_many(
            order_by={'dateCreated': 'desc'},
            take=50
        )
        print(f"✅ Direct find_many worked: {len(entries)} entries")
        
        print("6. Testing with where conditions...")
        entries = await prisma.entry.find_many(
            where={'isShared': True},
            order_by={'dateCreated': 'desc'},
            take=50
        )
        print(f"✅ find_many with where worked: {len(entries)} entries")
        
        await prisma.disconnect()
        
    except Exception as e:
        print(f"❌ Error at step: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_imports())