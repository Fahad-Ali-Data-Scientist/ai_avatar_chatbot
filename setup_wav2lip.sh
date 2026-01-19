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
echo "  GPU SETUP & VERIFICATION"
echo "========================================"
echo ""

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 Checking GPU availability..."
    echo ""
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo ""
    echo "✅ NVIDIA GPU detected!"
    echo ""
    
    # Check CUDA version
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
        echo "✅ CUDA installed: version $CUDA_VERSION"
    else
        echo "⚠️  CUDA toolkit not found (nvcc not in PATH)"
        echo "   GPU will still work with PyTorch's bundled CUDA"
    fi
    echo ""
    
    # Check Python GPU support
    echo "🔍 Verifying PyTorch GPU support..."
    python3 -c "import torch; print('✅ PyTorch version:', torch.__version__); print('✅ CUDA available:', torch.cuda.is_available()); print('✅ GPU count:', torch.cuda.device_count()); print('✅ Current GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ PyTorch GPU support verified!"
        echo ""
        echo "🚀 Wav2Lip will run on GPU for 5-10x faster generation!"
    else
        echo ""
        echo "⚠️  PyTorch not installed or no GPU support"
        echo ""
        echo "Installing PyTorch with GPU support..."
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        echo ""
        echo "✅ PyTorch with GPU support installed!"
    fi
else
    echo "⚠️  No NVIDIA GPU detected (nvidia-smi not found)"
    echo "   Wav2Lip will run on CPU (slower)"
fi

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
