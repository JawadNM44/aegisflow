#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════╗"
echo "║           AEGISFLOW - QUICK START           ║"
echo "╚══════════════════════════════════════════════╝"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check Python
PYTHON=""
for cmd in python3.12 python3 python; do
    if command -v $cmd &>/dev/null; then
        PYTHON=$cmd
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "✅ Using $($PYTHON --version)"

# Setup backend virtual environment
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    $PYTHON -m venv "$SCRIPT_DIR/backend/venv"
fi

echo "📦 Installing backend dependencies..."
source "$SCRIPT_DIR/backend/venv/bin/activate"
pip install -r "$SCRIPT_DIR/backend/requirements.txt" -q
deactivate

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Install frontend dependencies
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd "$SCRIPT_DIR/frontend"
    npm install --silent
    cd "$SCRIPT_DIR"
fi

echo ""
echo "🚀 Starting AEGISFLOW..."
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Start backend
source "$SCRIPT_DIR/backend/venv/bin/activate"
cd "$SCRIPT_DIR/backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
deactivate

sleep 2

# Start frontend
cd "$SCRIPT_DIR/frontend"
npx next dev -p 3000 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Trap to kill both on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait and check startup
sleep 3

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
    exit 1
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend running (PID: $FRONTEND_PID)"
fi

echo ""
echo "📋 Open http://localhost:3000 in your browser"
echo "   Press Ctrl+C to stop all services"

wait
