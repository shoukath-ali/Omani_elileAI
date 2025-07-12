#!/bin/bash

# Azure App Service startup script for Streamlit
echo "🚀 Starting Omani Mental Health Chatbot..."

# Set environment variables for Streamlit
export STREAMLIT_SERVER_PORT=${PORT:-8000}
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false

# Create Streamlit config directory if it doesn't exist
mkdir -p ~/.streamlit

# Create Streamlit config file
cat > ~/.streamlit/config.toml << EOF
[server]
port = ${PORT:-8000}
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 10

[browser]
gatherUsageStats = false
EOF

echo "✅ Starting Streamlit application on port ${PORT:-8000}..."

# Start Streamlit
streamlit run app.py --server.port=${PORT:-8000} --server.address=0.0.0.0 --server.headless=true 