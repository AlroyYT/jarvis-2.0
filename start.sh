#!/bin/bash

echo "🤖 Starting JARVIS..."
echo ""

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5000..."
cd backend
pip install -r requirements.txt -q
python app.py &
BACKEND_PID=$!
cd ..

sleep 2

# Start Next.js frontend
echo "🌐 Starting Next.js frontend on port 3000..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ JARVIS is online!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to shut down..."

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'JARVIS offline.'" EXIT
wait
