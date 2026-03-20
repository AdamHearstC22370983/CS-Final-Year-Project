#!/bin/bash

echo ""
echo "Stopping Skillgap..."
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_ROOT/.skillgap-pids"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file found. Nothing to stop."
  exit 0
fi

BACKEND_PID=$(sed -n '1p' "$PID_FILE")
FRONTEND_PID=$(sed -n '2p' "$PID_FILE")

if [ -n "$BACKEND_PID" ]; then
  kill "$BACKEND_PID" 2>/dev/null && echo "Backend stopped."
fi

if [ -n "$FRONTEND_PID" ]; then
  kill "$FRONTEND_PID" 2>/dev/null && echo "Frontend stopped."
fi

rm -f "$PID_FILE"

echo ""
echo "Skillgap has been stopped."