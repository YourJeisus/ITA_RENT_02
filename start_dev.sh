#!/bin/bash

# Start backend
echo "Starting backend..."
cd /Users/aleksandrbaranov/Documents/Work/MY_CODE_PROJECTS/ITA_RENT_02
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd /Users/aleksandrbaranov/Documents/Work/MY_CODE_PROJECTS/ITA_RENT_02/frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ Services started successfully!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait

