#!/bin/sh
set -e

if [ "$MODE" = "api" ]; then
    echo "Starting API server..."
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

elif [ "$MODE" = "bot" ]; then
    echo "Starting Telegram bot..."
    exec python bot.py

else
    # "both" — run bot in background, API in foreground
    echo "Starting Telegram bot in background..."
    python bot.py &

    echo "Starting API server..."
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
fi
