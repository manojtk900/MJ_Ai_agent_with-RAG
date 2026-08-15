#!/usr/bin/env bash
# =============================================================
# MJ AI Assistant — Setup Script
# =============================================================
set -e

echo "🚀 Setting up MJ AI Assistant..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.12+ required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js 20+ required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

# Copy env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created — please fill in your API keys"
fi

# Start infrastructure
echo "🐳 Starting Docker services..."
docker compose -f docker/docker-compose.yml up -d postgres redis

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until docker exec mj_postgres pg_isready -U mj_user -d mj_ai_assistant >/dev/null 2>&1; do
    sleep 2
done
echo "✅ PostgreSQL ready"

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
echo "✅ Backend ready"

# Frontend setup
echo "⚛️  Setting up React frontend..."
cd ../frontend
npm install
echo "✅ Frontend ready"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Start development:"
echo "  Backend:  cd backend && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo "  Docs:     http://localhost:8000/docs"
echo "  App:      http://localhost:5173"
