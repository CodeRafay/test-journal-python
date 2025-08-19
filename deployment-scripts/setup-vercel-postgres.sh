#!/bin/bash
# Vercel Postgres Setup Script

echo "🗄️  Vercel Postgres Database Setup"
echo "=================================="

# Check if user has Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "📋 Manual Setup Instructions:"
echo ""
echo "1. 🌐 Go to Vercel Dashboard:"
echo "   https://vercel.com/dashboard"
echo ""
echo "2. 📊 Create Database:"
echo "   → Click 'Storage' tab"
echo "   → Click 'Create Database'"  
echo "   → Select 'Postgres'"
echo "   → Name: journal-app-db"
echo "   → Region: Oregon (for Railway) or closest to your backend"
echo "   → Plan: Hobby (Free)"
echo "   → Click 'Create'"
echo ""
echo "3. 🔗 Get Connection String:"
echo "   → Click on your database"
echo "   → Go to 'Settings' → 'General'"
echo "   → Copy 'Postgres URL'"
echo "   → Should start with: postgresql://default:..."
echo ""

read -p "📝 Paste your Vercel Postgres connection string here: " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ No connection string provided. Exiting."
    exit 1
fi

# Validate connection string format
if [[ $DATABASE_URL != postgresql://* ]]; then
    echo "❌ Invalid connection string format. Should start with 'postgresql://'"
    exit 1
fi

echo "✅ Connection string received"

# Update backend .env file
echo "📝 Updating backend environment..."
cd backend

# Create or update .env file
cat > .env << EOF
DATABASE_URL="$DATABASE_URL"
CORS_ORIGINS="*"
ADMIN_PASSWORD="\$2b\$12\$sYkYSLH43UOgiXsxChneeua6AuMsnMsnbAJJn9QZizmPgrltvfJta"
VIEWER_PASSWORD="\$2b\$12\$SO5j2i7rGCj6.ZiXAi5F0Od9gPPYdDjT.gfE.6x05y0Q/W4bT8bL2"
EOF

echo "✅ Backend .env updated"

# Deploy schema to Vercel Postgres
echo "📊 Deploying database schema..."

# Check if Prisma is available
if ! command -v prisma &> /dev/null; then
    echo "📦 Installing Prisma CLI..."
    npm install -g prisma
fi

# Generate Prisma client
echo "🔄 Generating Prisma client..."
prisma generate

# Deploy schema
echo "🚀 Pushing schema to Vercel Postgres..."
prisma db push

if [ $? -eq 0 ]; then
    echo "✅ Database schema deployed successfully!"
    echo ""
    echo "🎯 Database Setup Complete:"
    echo "   Database: Vercel Postgres"
    echo "   Tables: entries (with indexes)"
    echo "   Connection: Verified"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Deploy your backend to Railway/Render"
    echo "2. Deploy your frontend to Vercel"
    echo "3. Update CORS settings with frontend URL"
else
    echo "❌ Failed to deploy schema. Please check your connection string."
    exit 1
fi

cd ..

echo ""
echo "🎉 Vercel Postgres setup completed!"
echo "You can now proceed with backend and frontend deployment."