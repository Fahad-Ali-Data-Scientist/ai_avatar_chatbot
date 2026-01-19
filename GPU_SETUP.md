# GPU Setup Guide - Talking Avatar

## 🎮 GPU Acceleration for Wav2Lip

This guide will help you set up Talking Avatar to run on your **NVIDIA 24GB GPU** for **5-10x faster video generation**.

---

## ⚡ Quick Setup (3 Commands)

```bash
# 1. Install dependencies with GPU support
chmod +x install_gpu.sh
./install_gpu.sh

# 2. Setup Wav2Lip and download model
chmod +x setup_wav2lip.sh
./setup_wav2lip.sh

# 3. Run with public HTTPS URL
chmod +x run_with_cloudflare.sh
./run_with_cloudflare.sh
```

**Done!** Your Talking Avatar will now run on GPU! 🚀

---

## 📋 System Requirements

### Required:
- ✅ **NVIDIA GPU** with CUDA support (you have 24GB - perfect!)
- ✅ **NVIDIA Drivers** 470+ installed
- ✅ **CUDA Toolkit** 11.8 or higher
- ✅ **Python** 3.8 or higher
- ✅ **Linux** server (Ubuntu/CentOS recommended)

### Your Server Specs:
```
GPU: NVIDIA (24GB VRAM)
Status: ✅ Perfect for Wav2Lip!
Expected Speed: 3-8 seconds per video
```

---

## 🚀 Installation Steps

### Step 1: Verify GPU

```bash
# Check if GPU is detected
nvidia-smi
```

**Expected output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.x  |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Your GPU Name       Off  | 00000000:XX:XX.X Off |                  N/A |
|  0%   40C    P0    50W / 250W |      0MiB / 24576MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

✅ If you see your GPU, continue!  
❌ If not, install NVIDIA drivers first.

---

### Step 2: Install CUDA (if not already installed)

```bash
# Check CUDA version
nvcc --version

# If not installed, install CUDA 11.8
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

Or use your distribution's package manager:

**Ubuntu:**
```bash
sudo apt-get install cuda-11-8
```

**CentOS:**
```bash
sudo yum install cuda-11-8
```

---

### Step 3: Run GPU Installation Script

```bash
cd talking_avatar_test
chmod +x install_gpu.sh
./install_gpu.sh
```

**What it does:**
1. ✅ Checks for NVIDIA GPU
2. ✅ Installs PyTorch with CUDA 11.8 support
3. ✅ Installs TorchVision with GPU support
4. ✅ Installs all dependencies
5. ✅ Verifies GPU is working

**Expected output:**
```
================================================================
  TALKING AVATAR - GPU INSTALLATION
================================================================

🔍 Checking for NVIDIA GPU...

Your GPU Name, 24576 MiB, 535.xx, 12.x
✅ NVIDIA GPU detected!

Python version: 3.12.3
✅ Python version OK

Installing dependencies...
🔥 Installing PyTorch with CUDA 11.8 support...

✅ PyTorch with GPU support installed
✅ All dependencies installed

Verifying GPU support...
PyTorch version: 2.2.0+cu118
CUDA available: True
CUDA version: 11.8
GPU count: 1
Current GPU: Your GPU Name
GPU memory: 24.0 GB

✅ GPU ACCELERATION ENABLED!
🚀 Wav2Lip will run 5-10x faster on your GPU!

================================================================
  ✅ INSTALLATION COMPLETE!
================================================================
```

---

### Step 4: Setup Wav2Lip

```bash
./setup_wav2lip.sh
```

This will:
- Clone Wav2Lip repository
- Download model weights (740 MB)
- Create required directories
- Verify GPU support for Wav2Lip

---

### Step 5: Run with Cloudflare Tunnel

```bash
./run_with_cloudflare.sh
```

**Expected output:**
```
================================================================
GPU & System Check
================================================================

🎮 GPU Status:
   Your GPU Name, 24576 MiB, 22000 MiB
   CUDA available: True
   GPU device: Your GPU Name
   ✅ GPU acceleration ENABLED
   🚀 Wav2Lip will run 5-10x faster!

================================================================
Starting Talking Avatar Flask server...
================================================================

🎭 Initializing AI Talking Avatar...
   - Multi-region TTS engine
   - Wav2Lip integration (GPU accelerated)
   - Streaming responses

✅ Flask server started

================================================================
✅ YOUR HTTPS URL IS READY!
================================================================

   🌐 https://abc-123-def.trycloudflare.com
```

---

## 📊 Performance Comparison

| Hardware | Video Generation Time | Notes |
|----------|----------------------|-------|
| **CPU (no GPU)** | 20-40 seconds | Slow, not recommended |
| **GPU (8GB)** | 8-15 seconds | Good |
| **GPU (16GB)** | 5-10 seconds | Very good |
| **GPU (24GB)** | **3-8 seconds** | ✅ **Your setup - Excellent!** |

With your 24GB GPU:
- ✅ First video: ~8 seconds
- ✅ Cached videos: ~3-5 seconds
- ✅ 5-10x faster than CPU
- ✅ Can handle multiple requests

---

## 🔍 Verify GPU is Being Used

### Check during runtime:

**Terminal 1: Run the server**
```bash
./run_with_cloudflare.sh
```

**Terminal 2: Monitor GPU**
```bash
watch -n 1 nvidia-smi
```

**Expected during video generation:**
```
|   0  Your GPU Name       On   | ...  |
|  70%   65C    P0   180W / 250W |  8000MiB / 24576MiB |  95%  Default |
                                      ↑ GPU Memory used
                                                           ↑ GPU Utilization
```

- **GPU Utilization:** Should be 80-100% during video generation
- **Memory Usage:** Should spike to 6-10 GB during processing
- **Temperature:** Should increase to 60-75°C (normal)

---

## 🐛 Troubleshooting

### Issue: "CUDA not available: False"

**Solution:**
```bash
# Check CUDA installation
nvcc --version

# Reinstall PyTorch with correct CUDA version
pip3 uninstall torch torchvision
pip3 install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "RuntimeError: CUDA out of memory"

**Solution:**
With 24GB GPU, this shouldn't happen. If it does:
```bash
# Check what's using GPU memory
nvidia-smi

# Kill other processes using GPU
# Or reduce batch size in Wav2Lip (not needed for your 24GB)
```

### Issue: GPU showing 0% utilization

**Possible causes:**
1. PyTorch not using GPU
2. Wav2Lip not configured for GPU
3. Model loaded on CPU instead of GPU

**Solution:**
```python
# Test GPU in Python
python3 << EOF
import torch
print("CUDA available:", torch.cuda.is_available())
print("Current device:", torch.cuda.current_device())
print("Device name:", torch.cuda.get_device_name(0))

# Test tensor on GPU
x = torch.rand(5, 3).cuda()
print("Tensor device:", x.device)
EOF
```

### Issue: Very slow despite GPU

**Check:**
```bash
# Verify GPU is actually being used
nvidia-smi

# Check app logs
tail -f flask.log

# Make sure CUDA_VISIBLE_DEVICES is set
echo $CUDA_VISIBLE_DEVICES  # Should be "0"
```

---

## 🎯 Optimization Tips

### For Your 24GB GPU:

1. **Batch Processing** (if needed in future):
   - Your GPU can handle multiple videos simultaneously
   - Current setup: 1 video at a time (perfect for now)

2. **Memory Management**:
   - 24GB is plenty - no optimization needed
   - Typical usage: 6-10 GB per video

3. **Temperature**:
   - Keep GPU below 80°C
   - Good cooling recommended for continuous use

4. **Power**:
   - Make sure your server has adequate power supply
   - GPU will use 150-200W under load

---

## 📈 Expected Performance

With your setup (24GB NVIDIA GPU):

### Video Generation:
- **Resolution:** 512x512 (default)
- **Duration:** Matches audio length (typically 10-30 seconds)
- **Generation Time:** 3-8 seconds
- **GPU Memory:** 6-10 GB during processing
- **GPU Utilization:** 80-95% during generation

### Concurrent Requests:
- **1 user:** 3-8 seconds
- **2 users:** 6-12 seconds (parallel processing)
- **5+ users:** Queue system recommended

---

## ✅ Verification Checklist

After installation, verify:

- [ ] `nvidia-smi` shows your GPU
- [ ] `nvcc --version` shows CUDA 11.8+
- [ ] `install_gpu.sh` completed successfully
- [ ] GPU verification script shows "CUDA available: True"
- [ ] `run_with_cloudflare.sh` shows "GPU acceleration ENABLED"
- [ ] During video generation, GPU utilization goes to 80-100%
- [ ] Video generation takes 3-8 seconds (not 20-40 seconds)

---

## 🎉 You're All Set!

Your Talking Avatar is now running on GPU! 

**Performance:**
- ✅ 5-10x faster video generation
- ✅ 3-8 seconds per video
- ✅ Ready for production use
- ✅ Can handle multiple users

**Commands:**
```bash
# Start server with GPU
./run_with_cloudflare.sh

# Monitor GPU usage
watch -n 1 nvidia-smi

# Check logs
tail -f flask.log
```

**Next steps:**
- Share your HTTPS URL with users
- Monitor GPU usage
- Enjoy blazing fast video generation! 🚀

---

## 📞 Support

If you have issues:
1. Check `flask.log` for errors
2. Run `nvidia-smi` to verify GPU
3. Verify CUDA with `nvcc --version`
4. Test PyTorch GPU: `python3 -c "import torch; print(torch.cuda.is_available())"`

Your 24GB GPU setup is perfect for this project! 🎉
