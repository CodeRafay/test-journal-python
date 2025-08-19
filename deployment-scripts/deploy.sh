#!/bin/bash
# Production Deployment Script for Journal App

echo "🚀 Starting Journal App Production Deployment..."

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: Please run this script from the app root directory"
    exit 1
fi

# Check for required tools
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

if ! command -v prisma &> /dev/null; then
    echo "📦 Installing Prisma CLI..."
    cd backend && npm install prisma && cd ..
fi

# Environment check
echo "🔍 Checking environment variables..."
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found"
    echo "Please create backend/.env with your DATABASE_URL and other variables"
    exit 1
fi

# Database setup
echo "🗄️  Setting up database schema..."
cd backend
export $(cat .env | xargs)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not set in backend/.env"
    echo "Please add your Vercel Postgres connection string"
    exit 1
fi

echo "📊 Pushing database schema to production..."
prisma db push --accept-data-loss

echo "✅ Database schema deployed successfully"
cd ..

# Frontend build
echo "🎨 Building frontend..."
cd frontend
yarn install
yarn build
cd ..

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update your frontend .env.production with the backend URL"
echo "2. Update backend CORS_ORIGINS with frontend URL"  
echo "3. Test your application at the provided URLs"
echo ""
echo "Admin login: 12345678"
echo "Viewer login: 87654321"