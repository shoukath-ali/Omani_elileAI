#!/bin/bash

# =============================================================================
# Omani Mental Health Voice-Enabled Chatbot - Azure Startup Script
# Supports both Streamlit web interface and WebSocket voice server
# =============================================================================

set -e  # Exit on any error

echo "🎤 Starting Omani Mental Health Voice-Enabled Assistant..."
echo "=============================================================="

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        print_success "$service_name is running on port $port"
        return 0
    else
        print_warning "$service_name is not responding on port $port"
        return 1
    fi
}

# Create logs directory
mkdir -p logs

# Set default ports
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}
WEBSOCKET_PORT=${WEBSOCKET_PORT:-8765}

print_status "Configuration:"
print_status "  - Streamlit Port: $STREAMLIT_PORT"
print_status "  - WebSocket Port: $WEBSOCKET_PORT"
print_status "  - App Title: ${APP_TITLE:-'Omani Voice Mental Health Assistant'}"

# Check Python version
print_status "Checking Python environment..."
python_version=$(python3 --version 2>&1)
print_status "Python version: $python_version"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Virtual environment detected: $VIRTUAL_ENV"
else
    print_warning "No virtual environment detected"
fi

# Install dependencies if needed
if [ ! -f ".dependencies_installed" ]; then
    print_status "Installing/updating dependencies..."
    pip install --no-cache-dir -r requirements.txt || {
        print_error "Failed to install dependencies"
        print_status "Trying with simplified requirements..."
        pip install streamlit python-dotenv requests openai anthropic
    }
    
    # Mark dependencies as installed
    touch .dependencies_installed
    print_success "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Load environment variables
if [ -f .env ]; then
    print_status "Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
    print_success "Environment variables loaded"
else
    print_warning "No .env file found. Using defaults."
fi

# Check Azure Speech Services configuration
print_status "Checking Azure Speech Services configuration..."
if [ -z "$AZURE_SPEECH_KEY" ]; then
    print_warning "AZURE_SPEECH_KEY not set. Voice features will be limited."
else
    print_success "Azure Speech Services configured"
fi

# Check AI model API keys
print_status "Checking AI model configurations..."
apis_configured=0

if [ -n "$OPENAI_API_KEY" ]; then
    print_success "OpenAI API configured"
    ((apis_configured++))
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    print_success "Anthropic API configured"
    ((apis_configured++))
fi

if [ $apis_configured -eq 0 ]; then
    print_error "No AI API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY"
    exit 1
fi

# Test voice service setup
print_status "Testing voice service setup..."
python3 -c "
from voice_service import test_voice_setup
result = test_voice_setup()
print(f'Voice service status: {result}')
" 2>/dev/null || print_warning "Voice service test failed (this is expected if Azure credentials are not set)"

# Function to start WebSocket server
start_websocket_server() {
    print_status "Starting WebSocket voice server on port $WEBSOCKET_PORT..."
    python3 websocket_service.py > logs/websocket.log 2>&1 &
    WEBSOCKET_PID=$!
    echo $WEBSOCKET_PID > logs/websocket.pid
    sleep 3
    
    if ps -p $WEBSOCKET_PID > /dev/null; then
        print_success "WebSocket server started (PID: $WEBSOCKET_PID)"
    else
        print_warning "WebSocket server failed to start (voice features will be limited)"
    fi
}

# Function to start Streamlit app
start_streamlit_app() {
    print_status "Starting Streamlit application on port $STREAMLIT_PORT..."
    
    # Streamlit configuration
    export STREAMLIT_SERVER_PORT=$STREAMLIT_PORT
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    export STREAMLIT_LOGGER_LEVEL=info
    
    # Start Streamlit
    streamlit run app.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false \
        --logger.level info > logs/streamlit.log 2>&1 &
    
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > logs/streamlit.pid
    print_status "Streamlit starting (PID: $STREAMLIT_PID)..."
}

# Function to monitor services
monitor_services() {
    print_status "Monitoring services..."
    sleep 10
    
    # Check Streamlit
    if check_service "Streamlit" $STREAMLIT_PORT; then
        print_success "Streamlit web interface is ready"
        print_status "  Access at: http://localhost:$STREAMLIT_PORT"
    fi
    
    # Check WebSocket (basic connection test)
    if netstat -ln 2>/dev/null | grep -q ":$WEBSOCKET_PORT "; then
        print_success "WebSocket server is listening"
        print_status "  WebSocket at: ws://localhost:$WEBSOCKET_PORT"
    else
        print_warning "WebSocket server may not be running"
    fi
}

# Function to handle shutdown
shutdown_services() {
    print_status "Shutting down services..."
    
    # Stop Streamlit
    if [ -f logs/streamlit.pid ]; then
        STREAMLIT_PID=$(cat logs/streamlit.pid)
        if ps -p $STREAMLIT_PID > /dev/null; then
            print_status "Stopping Streamlit (PID: $STREAMLIT_PID)"
            kill $STREAMLIT_PID
        fi
        rm -f logs/streamlit.pid
    fi
    
    # Stop WebSocket server
    if [ -f logs/websocket.pid ]; then
        WEBSOCKET_PID=$(cat logs/websocket.pid)
        if ps -p $WEBSOCKET_PID > /dev/null; then
            print_status "Stopping WebSocket server (PID: $WEBSOCKET_PID)"
            kill $WEBSOCKET_PID
        fi
        rm -f logs/websocket.pid
    fi
    
    print_success "All services stopped"
    exit 0
}

# Set up signal handlers
trap shutdown_services SIGINT SIGTERM

# Check if running in Azure App Service
if [ -n "$WEBSITE_SITE_NAME" ]; then
    print_status "Detected Azure App Service environment"
    export AZURE_DEPLOYMENT=true
    
    # Azure-specific configurations
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_PORT=${PORT:-$STREAMLIT_PORT}
    
    print_status "Azure configuration applied"
fi

# Main execution
print_status "Starting voice-enabled mental health assistant..."

# Start services based on environment
if [ "$VOICE_ENABLED" != "false" ]; then
    print_status "Voice interface enabled - starting both services"
    start_websocket_server
    start_streamlit_app
else
    print_status "Voice interface disabled - starting Streamlit only"
    start_streamlit_app
fi

# Monitor services
monitor_services

# Success message
print_success "🎤 Omani Mental Health Voice Assistant is running!"
echo ""
print_status "Services:"
print_status "  📱 Web Interface: http://localhost:$STREAMLIT_PORT"
if [ "$VOICE_ENABLED" != "false" ]; then
    print_status "  🎙️  Voice Server:  ws://localhost:$WEBSOCKET_PORT"
fi
echo ""
print_status "Features:"
print_status "  ✅ Mental health support in Omani Arabic context"
print_status "  ✅ Crisis detection with emergency contacts"
print_status "  ✅ Cultural sensitivity and Islamic values"
print_status "  ✅ Privacy-first design (no data storage)"
if [ -n "$AZURE_SPEECH_KEY" ]; then
    print_status "  ✅ Voice interface with Azure Speech Services"
    print_status "  ✅ Real-time speech processing"
else
    print_status "  ⚠️  Voice interface limited (Azure Speech not configured)"
fi
echo ""
print_status "Emergency Contact: 9999 (Oman Emergency Services)"
echo ""
print_status "Press Ctrl+C to stop all services"

# Keep script running and monitor services
while true; do
    sleep 30
    
    # Check if Streamlit is still running
    if [ -f logs/streamlit.pid ]; then
        STREAMLIT_PID=$(cat logs/streamlit.pid)
        if ! ps -p $STREAMLIT_PID > /dev/null; then
            print_error "Streamlit has stopped unexpectedly. Restarting..."
            start_streamlit_app
        fi
    fi
    
    # Check if WebSocket server is still running (if enabled)
    if [ "$VOICE_ENABLED" != "false" ] && [ -f logs/websocket.pid ]; then
        WEBSOCKET_PID=$(cat logs/websocket.pid)
        if ! ps -p $WEBSOCKET_PID > /dev/null; then
            print_warning "WebSocket server has stopped. Restarting..."
            start_websocket_server
        fi
    fi
done 