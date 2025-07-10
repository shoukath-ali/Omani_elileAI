#!/bin/bash

# Startup script for Azure Web App
echo "Starting Omani Mental Health Chatbot..."

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
fi

# Start Streamlit app
echo "Starting Streamlit on port $PORT..."
python -m streamlit run app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false 