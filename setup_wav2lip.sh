#!/bin/bash

# Wav2Lip Setup Script
# This script clones Wav2Lip repository and downloads model weights

echo "========================================"
echo "  WAV2LIP SETUP SCRIPT"
echo "========================================"
echo ""

# Check if Wav2Lip already exists
if [ -d "Wav2Lip" ]; then
    echo "⚠️  Wav2Lip directory already exists"
    read -p "Do you want to remove and reinstall? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing Wav2Lip directory..."
        rm -rf Wav2Lip
    else
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

echo "📥 Cloning Wav2Lip repository..."
git clone https://github.com/Rudrabha/Wav2Lip.git

if [ $? -ne 0 ]; then
    echo "❌ Failed to clone Wav2Lip repository"
    exit 1
fi

echo "✅ Wav2Lip cloned successfully"
echo ""

# Navigate to Wav2Lip directory
cd Wav2Lip

# Create checkpoints directory
echo "📁 Creating checkpoints directory..."
mkdir -p checkpoints

# Create temp directory (required for audio processing)
echo "📁 Creating temp directory..."
mkdir -p temp

# Create results directory
echo "📁 Creating results directory..."
mkdir -p results

echo ""
echo "📥 Downloading model weights..."
echo "   Source: https://huggingface.co/Nekochu/Wav2Lip"
echo "   Size: ~740 MB (this may take a few minutes)"
echo ""

# Download model weights
wget "https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth" -O "checkpoints/wav2lip_gan.pth"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to download model weights"
    echo ""
    echo "Please download manually from:"
    echo "https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth"
    echo ""
    echo "Save to: Wav2Lip/checkpoints/wav2lip_gan.pth"
    exit 1
fi

echo ""
echo "✅ Model weights downloaded successfully"
echo ""

# Verify the download
if [ -f "checkpoints/wav2lip_gan.pth" ]; then
    FILE_SIZE=$(ls -lh checkpoints/wav2lip_gan.pth | awk '{print $5}')
    echo "✅ Model file verified: $FILE_SIZE"
else
    echo "❌ Model file not found!"
    exit 1
fi

# Go back to project root
cd ..

echo ""
echo "========================================"
echo "  ✅ WAV2LIP SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Created directories:"
echo "  ✓ Wav2Lip/checkpoints/"
echo "  ✓ Wav2Lip/temp/"
echo "  ✓ Wav2Lip/results/"
echo ""
echo "Downloaded files:"
echo "  ✓ Wav2Lip/checkpoints/wav2lip_gan.pth"
echo ""
echo "Next steps:"
echo "  1. Install Python dependencies: pip install -r requirements.txt"
echo "  2. Run the notebook: jupyter notebook talking_avatar_complete.ipynb"
echo "  3. Or run the web server: python app.py"
echo ""
echo "========================================"
