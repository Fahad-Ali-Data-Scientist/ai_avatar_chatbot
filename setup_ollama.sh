#!/bin/bash

echo "================================================================"
echo "Ollama + Gemma 9B Model Setup"
echo "================================================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is designed for Linux servers"
    echo "   For other OS, visit: https://ollama.ai"
    exit 1
fi

# Check if ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
    ollama --version
else
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Failed to install Ollama"
        exit 1
    fi
fi

echo ""
echo "================================================================"
echo "Starting Ollama Service"
echo "================================================================"
echo ""

# Start ollama service in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama service..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 3
    echo "✅ Ollama service started"
else
    echo "✅ Ollama service already running"
fi

echo ""
echo "================================================================"
echo "Downloading Gemma 2 9B Model (Instruct)"
echo "================================================================"
echo ""
echo "⚠️  This will download ~5.5GB of data"
echo "   Please ensure you have enough disk space and bandwidth"
echo ""

# Pull the gemma2:9b-instruct-q4_K_M model (quantized for better performance)
echo "📥 Pulling gemma2:9b-instruct-q4_K_M model..."
ollama pull gemma2:9b-instruct-q4_K_M

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Gemma 2 9B model downloaded successfully"
else
    echo ""
    echo "❌ Failed to download model"
    echo "   Trying alternative: gemma:7b-instruct..."
    ollama pull gemma:7b-instruct
fi

echo ""
echo "================================================================"
echo "Testing Model"
echo "================================================================"
echo ""

# Test the model
echo "🧪 Testing Gemma model with a simple query..."
echo ""
ollama run gemma2:9b-instruct-q4_K_M "Say hello in one sentence" 2>/dev/null || ollama run gemma:7b-instruct "Say hello in one sentence"

echo ""
echo "================================================================"
echo "Ollama API Information"
echo "================================================================"
echo ""
echo "📡 Ollama API endpoint: http://localhost:11434"
echo ""
echo "Available models:"
ollama list

echo ""
echo "================================================================"
echo "Setup Complete! ✅"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Ollama is running on: http://localhost:11434"
echo "  2. Update app.py to use USE_OLLAMA = True"
echo "  3. Run: python app.py"
echo ""
echo "To test manually:"
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"gemma2:9b-instruct-q4_K_M\",\"prompt\":\"Hello\"}'"
echo ""
echo "To stop Ollama service:"
echo "  pkill ollama"
echo ""
echo "================================================================"
