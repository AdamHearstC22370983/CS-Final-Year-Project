#!/bin/bash

echo ""
echo "============================="
echo " Starting Skillgap..."
echo "============================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PATH="$PROJECT_ROOT/backend"
FRONTEND_PATH="$PROJECT_ROOT/frontend"
PID_FILE="$PROJECT_ROOT/.skillgap-pids"

# Adjust this if the venv is somewhere else
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
  echo "Backend Python executable not found at:"
  echo "$VENV_PYTHON"
  exit 1
fi

if [ ! -d "$BACKEND_PATH" ]; then
  echo "Backend folder not found."
  exit 1
fi

if [ ! -d "$FRONTEND_PATH" ]; then
  echo "Frontend folder not found."
  exit 1
fi

echo "Starting backend..."
cd "$BACKEND_PATH" || exit 1
"$VENV_PYTHON" -m uvicorn app.main:app --reload >/dev/null 2>&1 &
BACKEND_PID=$!

sleep 2

if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "Backend failed to start."
  exit 1
fi

echo "Backend started."
echo "API docs: http://127.0.0.1:8000/docs"
echo ""

echo "Starting frontend..."
cd "$FRONTEND_PATH" || exit 1
npm run dev >/dev/null 2>&1 &
FRONTEND_PID=$!

sleep 5

if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
  echo "Frontend failed to start."
  exit 1
fi

echo "$BACKEND_PID" > "$PID_FILE"
echo "$FRONTEND_PID" >> "$PID_FILE"

echo "Frontend started."
echo ""
echo "Skillgap is now running."
echo ""
echo "Links:"
echo " - Website:  http://localhost:5173"
echo " - Backend:  http://127.0.0.1:8000"
echo " - API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Use ./stop-skillgap.sh to stop both services."
echo ""

open "http://localhost:5173"