#!/bin/bash

# Installation script for Talking Avatar with GPU support
# For servers with NVIDIA GPU (24GB recommended)

echo "================================================================"
echo "  TALKING AVATAR - GPU INSTALLATION"
echo "================================================================"
echo ""

# Check for NVIDIA GPU
echo "🔍 Checking for NVIDIA GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ Error: nvidia-smi not found"
    echo "   This script requires an NVIDIA GPU"
    echo "   For CPU installation, use: pip install -r requirements.txt"
    exit 1
fi

echo ""
nvidia-smi --query-gpu=name,memory.total,driver_version,cuda_version --format=csv,noheader
echo ""
echo "✅ NVIDIA GPU detected!"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "❌ Error: Python 3.8+ required"
    exit 1
fi

echo "✅ Python version OK"
echo ""

# Ask for confirmation
echo "================================================================"
echo "This will install:"
echo "  - PyTorch with CUDA 11.8 support"
echo "  - TorchVision with GPU support"
echo "  - All Talking Avatar dependencies"
echo "  - Wav2Lip requirements"
echo ""
read -p "Continue? [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]*$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "================================================================"
echo "Installing dependencies..."
echo "================================================================"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip
echo ""

# Install PyTorch with GPU support (CUDA 11.8)
echo "🔥 Installing PyTorch with CUDA 11.8 support..."
echo "   This may take a few minutes..."
echo ""
pip3 install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118

if [ $? -ne 0 ]; then
    echo "❌ Failed to install PyTorch with GPU support"
    exit 1
fi

echo ""
echo "✅ PyTorch with GPU support installed"
echo ""

# Install other dependencies (excluding torch/torchvision)
echo "📦 Installing other dependencies..."
echo ""
pip3 install flask==3.0.0 \
    edge-tts==6.1.10 \
    gTTS==2.5.1 \
    pyttsx3==2.90 \
    pydub==0.25.1 \
    opencv-python==4.9.0.80 \
    numpy==1.26.4 \
    pillow==10.2.0 \
    imageio==2.33.1 \
    scipy==1.12.0 \
    librosa==0.9.2 \
    numba==0.56.4 \
    audioread \
    resampy \
    ffmpeg-python

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ All dependencies installed"
echo ""

# Verify GPU support
echo "================================================================"
echo "Verifying GPU support..."
echo "================================================================"
echo ""

python3 << EOF
import torch
import sys

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU count:", torch.cuda.device_count())
    print("Current GPU:", torch.cuda.get_device_name(0))
    print("GPU memory:", f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print("")
    print("✅ GPU ACCELERATION ENABLED!")
    print("🚀 Wav2Lip will run 5-10x faster on your GPU!")
else:
    print("")
    print("❌ CUDA not available - GPU acceleration disabled")
    print("Please check:")
    print("  1. NVIDIA drivers are installed")
    print("  2. CUDA toolkit is installed")
    print("  3. PyTorch CUDA version matches your CUDA version")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  GPU verification failed"
    echo "   Installation completed but GPU may not work"
    exit 1
fi

echo ""
echo "================================================================"
echo "  ✅ INSTALLATION COMPLETE!"
echo "================================================================"
echo ""
echo "GPU Status:"
echo "  ✅ PyTorch with CUDA support installed"
echo "  ✅ GPU acceleration verified"
echo "  ✅ All dependencies installed"
echo ""
echo "Next steps:"
echo "  1. Setup Wav2Lip: ./setup_wav2lip.sh"
echo "  2. Run with Cloudflare: ./run_with_cloudflare.sh"
echo ""
echo "Performance:"
echo "  🚀 Video generation: ~3-8 seconds (with 24GB GPU)"
echo "  🚀 5-10x faster than CPU"
echo ""
echo "================================================================"
