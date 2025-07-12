#!/bin/bash

# Voice-Only Omani Arabic Mental Health Chatbot
# Azure App Service Startup Script

echo "🧠 Starting Omani Mental Health Chatbot..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Install FFmpeg for audio processing (if not available)
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    apt-get update
    apt-get install -y ffmpeg
fi

# Install system dependencies for audio processing
apt-get install -y libsndfile1

# Set Streamlit configuration
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=localhost
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Set application configuration
export APP_NAME="Omani Mental Health Assistant"
export MAX_RESPONSE_TIME=15
export ENABLE_CRISIS_DETECTION=true
export PRIMARY_LANGUAGE=ar-OM
export CULTURAL_CONTEXT=gulf_arab

# Create logs directory
mkdir -p /home/site/wwwroot/logs

# Start the Streamlit application
echo "🚀 Starting Streamlit server on port 8000..."
cd /home/site/wwwroot
python -m streamlit run app.py --server.port=8000 --server.address=localhost --server.enableCORS=false --server.enableXsrfProtection=false 