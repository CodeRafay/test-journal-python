# Vercel Postgres Setup Guide

## 1. Create Vercel Postgres Database

### Step 1: Login to Vercel Dashboard
- Go to [vercel.com](https://vercel.com)
- Navigate to your dashboard

### Step 2: Create Storage Database
1. Click **"Storage"** tab in your dashboard
2. Click **"Create Database"**
3. Select **"Postgres"**
4. Choose database name: `journal-app-db`
5. Select region closest to your users
6. Click **"Create"**

### Step 3: Get Connection Details
After creation, you'll see:
- **Database URL**: Copy the full connection string
- **Connection pooling**: Enable for better performance

## 2. Update Environment Variables

### Backend .env file:
```env
DATABASE_URL="your-vercel-postgres-connection-string"
DB_NAME="journal_db"
CORS_ORIGINS="*"
ADMIN_PASSWORD="$2b$12$sYkYSLH43UOgiXsxChneeua6AuMsnMsnbAJJn9QZizmPgrltvfJta"
VIEWER_PASSWORD="$2b$12$SO5j2i7rGCj6.ZiXAi5F0Od9gPPYdDjT.gfE.6x05y0Q/W4bT8bL2"
```

## 3. Deploy Database Schema

### Run Prisma Migration:
```bash
cd backend
prisma migrate dev --name init
```

### Or use Prisma Push for development:
```bash
cd backend  
prisma db push
```

## 4. Verify Setup

### Test Database Connection:
```bash
cd backend
python -c "
from prisma import Prisma
import asyncio

async def test_connection():
    prisma = Prisma()
    await prisma.connect()
    print('✅ Connected to Vercel Postgres!')
    await prisma.disconnect()

asyncio.run(test_connection())
"
```

## 5. Production Deployment

### For Vercel Deployment:
1. Push your code to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard:
   - `DATABASE_URL` (from Vercel Storage)
   - All other variables from your .env file

### For Railway/Render:
1. Use same environment variables
2. Ensure Prisma generate runs during build
3. Database schema will be auto-created

## 6. Database Administration

### Prisma Studio (Optional):
```bash
cd backend
prisma studio
```
- Opens web interface to view/edit data
- Great for debugging and testing

## Notes:
- Vercel Postgres includes connection pooling
- Automatic backups included
- Scales with your application usage
- Compatible with all major deployment platforms