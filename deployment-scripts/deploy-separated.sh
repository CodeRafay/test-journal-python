#!/bin/bash
# Separated Architecture Deployment Script
# Frontend: Vercel | Backend: Railway/Render | Database: Vercel Postgres

echo "🚀 Starting Separated Architecture Deployment..."

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: Please run this script from the app root directory"
    exit 1
fi

# Check for required tools
echo "🔍 Checking required tools..."

if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
    echo "⚠️  Please run 'railway login' before continuing"
fi

# Function to deploy backend to Railway
deploy_backend_railway() {
    echo "🚂 Deploying backend to Railway..."
    cd backend
    
    # Check if Railway project exists
    if [ ! -f ".railway" ]; then
        echo "🆕 Creating new Railway project..."
        railway login
        railway new journal-app-backend
    fi
    
    # Deploy to Railway
    railway deploy
    
    # Get the URL
    echo "📍 Getting Railway app URL..."
    RAILWAY_URL=$(railway status --json | grep -o 'https://[^"]*')
    echo "✅ Backend deployed to: $RAILWAY_URL"
    
    cd ..
    return 0
}

# Function to deploy backend to Render
deploy_backend_render() {
    echo "🎨 For Render deployment:"
    echo "1. Go to https://render.com/dashboard"
    echo "2. Create new Web Service"
    echo "3. Connect your repository"
    echo "4. Use these settings:"
    echo "   - Environment: Python 3"
    echo "   - Root Directory: backend"
    echo "   - Build Command: pip install -r requirements.txt && prisma generate"
    echo "   - Start Command: uvicorn server:app --host 0.0.0.0 --port \$PORT"
    echo "5. Add environment variables from backend/.env.production"
    echo ""
    read -p "Enter your Render backend URL (e.g., https://yourapp.onrender.com): " RENDER_URL
    echo "✅ Backend URL set to: $RENDER_URL"
    return 0
}

# Ask user which backend platform to use
echo "🤔 Which backend platform do you want to use?"
echo "1) Railway (Recommended - easier CLI deployment)"
echo "2) Render (Manual setup via dashboard)"
read -p "Choose (1 or 2): " BACKEND_CHOICE

case $BACKEND_CHOICE in
    1)
        deploy_backend_railway
        BACKEND_URL=$RAILWAY_URL
        ;;
    2)
        deploy_backend_render
        BACKEND_URL=$RENDER_URL
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

# Update frontend environment with backend URL
echo "🎨 Updating frontend environment..."
cd frontend
echo "REACT_APP_BACKEND_URL=$BACKEND_URL" > .env.production
echo "WDS_SOCKET_PORT=443" >> .env.production
echo "GENERATE_SOURCEMAP=false" >> .env.production

# Deploy frontend to Vercel
echo "🚀 Deploying frontend to Vercel..."
vercel --prod

# Get frontend URL
FRONTEND_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
echo "✅ Frontend deployed to: $FRONTEND_URL"

cd ..

# Instructions for updating CORS
echo ""
echo "🔧 Final Configuration Steps:"
echo "================================"
echo "1. Update backend CORS settings:"

if [ $BACKEND_CHOICE -eq 1 ]; then
    echo "   Run: railway variables set CORS_ORIGINS=\"$FRONTEND_URL\""
else
    echo "   In Render dashboard, set CORS_ORIGINS = $FRONTEND_URL"
fi

echo ""
echo "2. Set these environment variables in your backend platform:"
echo "   DATABASE_URL = (your Vercel Postgres connection string)"
echo "   CORS_ORIGINS = $FRONTEND_URL"
echo "   ADMIN_PASSWORD = \$2b\$12\$sYkYSLH43UOgiXsxChneeua6AuMsnMsnbAJJn9QZizmPgrltvfJta"
echo "   VIEWER_PASSWORD = \$2b\$12\$SO5j2i7rGCj6.ZiXAi5F0Od9gPPYdDjT.gfE.6x05y0Q/W4bT8bL2"
echo ""
echo "3. Test your deployment:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL/api"
echo "   Admin login: 12345678"
echo "   Viewer login: 87654321"
echo ""
echo "🎉 Deployment script completed!"
echo "Run the verification script to test everything:"
echo "python deployment-scripts/verify-deployment.py $BACKEND_URL"