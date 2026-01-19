#!/bin/bash

# Run Talking Avatar with Cloudflare Tunnel
# This script starts the Flask app and creates a public HTTPS URL

echo "========================================"
echo "  TALKING AVATAR - CLOUDFLARE TUNNEL"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.12+"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✓ Using Python: $PYTHON_CMD"
echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "   Please run this script from the talking_avatar_test directory"
    exit 1
fi

# Check if cloudflared is installed
echo "🔍 Checking for cloudflared..."
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found. Installing..."
    echo ""
    
    # Detect OS and install cloudflared
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "📥 Installing cloudflared for Linux..."
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /tmp/cloudflared
        sudo mv /tmp/cloudflared /usr/local/bin/
        sudo chmod +x /usr/local/bin/cloudflared
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "📥 Installing cloudflared for macOS..."
        if command -v brew &> /dev/null; then
            brew install cloudflared
        else
            echo "❌ Homebrew not found. Please install cloudflared manually:"
            echo "   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
            exit 1
        fi
        
    else
        # Windows or other
        echo "❌ Automatic installation not supported for your OS"
        echo ""
        echo "Please install cloudflared manually:"
        echo "  Windows: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        echo "  Linux:   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        echo "  macOS:   brew install cloudflared"
        echo ""
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ cloudflared installed successfully"
    else
        echo "❌ Failed to install cloudflared"
        exit 1
    fi
else
    echo "✅ cloudflared already installed"
fi

echo ""
echo "========================================"
echo "  STARTING SERVICES"
echo "========================================"
echo ""

# Kill any existing Flask processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null
pkill -f "cloudflared.*tunnel" 2>/dev/null
sleep 2

# Start Flask app in background
echo "🚀 Starting Flask application on port 5000..."
$PYTHON_CMD app.py > flask_app.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to start
echo "⏳ Waiting for Flask to start..."
sleep 5

# Check if Flask is running
if ! ps -p $FLASK_PID > /dev/null 2>&1; then
    echo "❌ Flask failed to start. Check flask_app.log for errors:"
    tail -n 20 flask_app.log
    exit 1
fi

# Check if port 5000 is listening
if ! netstat -tuln 2>/dev/null | grep -q ":5000 " && ! ss -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "⚠️  Port 5000 might not be listening, but continuing..."
fi

echo "✅ Flask app started (PID: $FLASK_PID)"
echo ""

# Start Cloudflare tunnel
echo "🌐 Starting Cloudflare Tunnel..."
echo "   This will create a public HTTPS URL for your app"
echo ""
echo "========================================"
echo ""

cloudflared tunnel --url http://localhost:5000

# This line will only execute when cloudflared is stopped (Ctrl+C)
echo ""
echo ""
echo "========================================"
echo "  SHUTTING DOWN"
echo "========================================"
echo ""

echo "🛑 Stopping Flask app (PID: $FLASK_PID)..."
kill $FLASK_PID 2>/dev/null

echo "🧹 Cleaning up..."
pkill -f "cloudflared.*tunnel" 2>/dev/null

echo ""
echo "✅ All services stopped"
echo ""
echo "Log file saved: flask_app.log"
echo ""
echo "========================================"
