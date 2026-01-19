#!/bin/bash

echo "================================================================"
echo "TALKING AVATAR CHATBOT - HTTPS Setup (No Signup Required!)"
echo "================================================================"
echo ""
echo "This uses Cloudflare Tunnel - No account needed!"
echo "Creates a public HTTPS URL for your AI Talking Avatar"
echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "   Please run this script from: talking_avatar_test/"
    exit 1
fi

# Check if Wav2Lip is setup
if [ ! -d "Wav2Lip" ]; then
    echo "⚠️  Warning: Wav2Lip not found"
    echo "   Run: ./setup_wav2lip.sh to install"
    echo ""
    read -p "Continue without Wav2Lip? (audio-only mode) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Please run: ./setup_wav2lip.sh first"
        exit 1
    fi
    echo "⚠️  Running in AUDIO-ONLY mode (no video generation)"
    echo ""
fi

# Check if requirements are installed
if ! python3 -c "from gtts import gTTS" 2>/dev/null; then
    echo "⚠️  Warning: Dependencies might not be installed"
    echo "   Run: pip install -r requirements.txt"
    echo ""
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Installing cloudflared..."
    echo ""
    
    # Detect architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared
    else
        echo "Unsupported architecture: $ARCH"
        exit 1
    fi
    
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/
    
    echo "✅ cloudflared installed!"
    echo ""
fi

echo "================================================================"
echo "Starting Talking Avatar Flask server..."
echo "================================================================"
echo ""
echo "🎭 Initializing AI Talking Avatar..."
echo "   - Multi-region TTS engine"
echo "   - Wav2Lip integration"
echo "   - Streaming responses"
echo ""

# Start Flask in background
python3 app.py > flask.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to start
sleep 5

echo "✅ Flask server started"
echo ""
echo "================================================================"
echo "Starting HTTPS tunnel..."
echo "================================================================"
echo ""
echo "⏳ Getting your HTTPS URL... (takes 5-10 seconds)"
echo ""

# Start cloudflared and capture output
cloudflared tunnel --url http://localhost:5000 > tunnel.log 2>&1 &
TUNNEL_PID=$!

# Wait for URL to be ready
sleep 8

# Extract URL from log
HTTPS_URL=$(grep -o 'https://.*trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$HTTPS_URL" ]; then
    echo "⚠️  Could not auto-detect URL"
    echo "Checking tunnel log..."
    cat tunnel.log | grep https://
else
    echo ""
    echo "================================================================"
    echo "✅ YOUR HTTPS URL IS READY!"
    echo "================================================================"
    echo ""
    echo "   🌐 $HTTPS_URL"
    echo ""
    echo "================================================================"
    echo ""
    echo "📱 SHARE THIS URL TO ACCESS YOUR TALKING AVATAR!"
    echo ""
    echo "Features:"
    echo "  ✅ Multi-region TTS (works everywhere)"
    echo "  ✅ Edge TTS → Google TTS auto-fallback"
    echo "  ✅ Wav2Lip lip-sync animation"
    echo "  ✅ Streaming responses"
    echo "  ✅ Works on mobile and desktop"
    echo ""
    echo "How to use:"
    echo "  1. Open the URL above in your browser"
    echo "  2. Type your question in the text box"
    echo "  3. Click 'Ask' or press Enter"
    echo "  4. Watch your AI avatar respond with video!"
    echo ""
    echo "================================================================"
    echo ""
    echo "📊 Server Status:"
    echo "   Flask PID: $FLASK_PID"
    echo "   Tunnel PID: $TUNNEL_PID"
    echo ""
    echo "📝 Logs:"
    echo "   Flask log: flask.log"
    echo "   Tunnel log: tunnel.log"
    echo ""
    echo "🛑 To stop: Press Ctrl+C"
    echo ""
    echo "💡 Tips:"
    echo "   - If TTS fails, it auto-switches to Google TTS"
    echo "   - First video generation takes 15-30 seconds"
    echo "   - Subsequent videos are faster (cached)"
    echo "   - Check flask.log if you encounter errors"
    echo ""
    echo "================================================================"
fi

# Cleanup function
cleanup() {
    echo ""
    echo "================================================================"
    echo "Shutting down Talking Avatar server..."
    echo "================================================================"
    echo ""
    kill $FLASK_PID 2>/dev/null
    kill $TUNNEL_PID 2>/dev/null
    echo "✓ Flask server stopped"
    echo "✓ Cloudflare tunnel stopped"
    echo ""
    echo "Logs saved (not deleted for debugging):"
    echo "  - flask.log"
    echo "  - tunnel.log"
    echo ""
    echo "✅ Shutdown complete. Thank you for using Talking Avatar!"
    echo ""
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
