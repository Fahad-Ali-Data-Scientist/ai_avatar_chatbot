# Talking Avatar Chatbot - Testing Module

Complete implementation of a talking avatar chatbot that converts text responses into lip-synced videos.

## 🌍 NEW: Multi-Region TTS Support

**✅ Fixed:** Edge TTS 403 errors in blocked regions  
**✅ Works globally:** Automatic fallback to Google TTS if Edge TTS is blocked  
**✅ Zero configuration:** Automatically detects and uses the best available engine  
**✅ Offline mode:** Falls back to offline TTS if no internet connection

## 📁 Project Structure

```
talking_avatar_test/
├── talking_avatar_complete.ipynb  # Main notebook with all code
├── README.md                       # This file
├── outputs/                        # Generated files (created automatically)
│   ├── sample_avatar.jpg
│   ├── response_audio.mp3
│   └── talking_avatar.mp4
└── Wav2Lip/                        # Clone here (instructions below)
    └── checkpoints/
        └── wav2lip_gan.pth
```

## 🚀 Quick Start

### 1. Prerequisites

Make sure you have installed all required packages:

```bash
# Install from requirements.txt (RECOMMENDED)
pip install -r requirements.txt

# Or install manually:
pip install flask edge-tts gTTS pyttsx3 pydub opencv-python numpy torch torchvision pillow imageio scipy
```

**Python Version:** 3.12.3

**New Dependencies:**
- `gTTS` - Google Text-to-Speech (fallback for blocked regions)
- `pyttsx3` - Offline TTS (works without internet)
- `pydub` - Audio processing and merging

### 2. Setup Wav2Lip

```bash
# Navigate to the project folder
cd "C:\Users\Fahad Ali\Documents\jubyter\talking_avatar_test"

# Clone Wav2Lip repository
git clone https://github.com/Rudrabha/Wav2Lip.git

# Download the model checkpoint
cd Wav2Lip
mkdir -p checkpoints
# Download from HuggingFace (more reliable)
# Use wget or download manually from:
# https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth
# Save to: Wav2Lip/checkpoints/wav2lip_gan.pth
```

### 3. Run the Notebook

1. Open Jupyter Notebook or JupyterLab
2. Navigate to `talking_avatar_complete.ipynb`
3. Run all cells in order
4. Test with the provided sample or upload your own avatar image

## 📝 What's Inside the Notebook

### Cell-by-Cell Breakdown:

1. **Import Libraries** - All required dependencies
2. **Configuration** - Setup paths and check installations
3. **Text Generator** - Hardcoded chatbot with 50-word chunking
4. **TTS Module** - Edge-TTS for audio generation
5. **Lip-Sync Module** - Wav2Lip for video generation
6. **Sample Avatar** - Creates a placeholder image
7. **Complete Pipeline** - End-to-end integration
8. **Test Section** - Run the complete pipeline
9. **Custom Testing** - Test with your own avatar

## 🎯 Features

✅ **Hardcoded Text Generation** - Returns responses chunk by chunk (50 words)

✅ **🌍 Multi-Region TTS** - Automatic fallback between Edge TTS, Google TTS, and Offline TTS
   - **Edge TTS** - Highest quality (tries first)
   - **Google TTS** - Good quality, works globally (automatic fallback)
   - **Offline TTS** - Works without internet (last resort)

✅ **Lip-Sync Animation** - Wav2Lip for realistic talking avatars

✅ **Complete Pipeline** - Automated end-to-end processing

✅ **Performance Tracking** - Timing information for each stage

✅ **Regional Compatibility** - No more 403 errors! Works in ALL regions

## ⚙️ Configuration Options

### Available Questions (Hardcoded):
- "what is ai"
- "what is machine learning"
- "hello"
- Any other question (gets default response)

### Available Voices:
- `en-US-AriaNeural` (Female) - Default
- `en-US-GuyNeural` (Male)
- `en-US-JennyNeural` (Female)
- `en-GB-SoniaNeural` (British Female)
- `en-GB-RyanNeural` (British Male)

### Avatar Requirements:
- Clear, frontal face photo
- Good lighting
- Resolution: 512x512 or higher
- Neutral expression works best

## 📊 Expected Performance

| Stage | Time | Notes |
|-------|------|-------|
| Text Generation | < 1s | Hardcoded responses |
| Audio Conversion | 1-3s | Edge-TTS (cloud-based) |
| Video Generation | 10-30s | CPU (5-10s with GPU) |
| **Total** | **15-35s** | Per response |

## 🔧 Troubleshooting

### Wav2Lip Not Found
```python
# In the notebook, update the path:
WAV2LIP_PATH = Path("./Wav2Lip")  # Adjust if needed
```

### Model Checkpoint Missing
Download from: https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth
Save to: `Wav2Lip/checkpoints/wav2lip_gan.pth`

### Audio Issues
- Ensure ffmpeg is installed: `apt-get install ffmpeg` (Linux) or download for Windows
- Check internet connection (Edge-TTS and Google TTS require online access)
- If you see "Edge TTS failed", the system will automatically switch to Google TTS
- For offline mode, install pyttsx3: `pip install pyttsx3`

### TTS 403 Error (FIXED!)
**Problem:** Edge TTS blocked in your region (403 Forbidden)  
**Solution:** ✅ Already fixed! The system now automatically:
1. Tries Edge TTS first
2. Falls back to Google TTS if Edge TTS fails
3. Uses offline TTS if both online options fail

**To force a specific engine:**
```python
# Force Google TTS (if Edge TTS is blocked)
tts = TextToSpeechEngine(preferred_engine="gtts")

# Force offline TTS (no internet needed)
tts = TextToSpeechEngine(preferred_engine="pyttsx3")

# Auto mode (default, recommended)
tts = TextToSpeechEngine(preferred_engine="auto")
```

### Video Generation Fails
- Verify avatar image has a clear, visible face
- Try with a different image
- Check Wav2Lip logs in the notebook output

## 🎨 Customization

### Add Your Own Questions:

Edit the `hardcoded_chatbot()` function in Cell 3:

```python
responses = {
    "your question": """Your custom response here...""",
    # ... more questions
}
```

### Change Voice:

Update the `TTS_VOICE` variable in Cell 8:

```python
TTS_VOICE = "en-US-GuyNeural"  # Male voice
```

### Use Your Own Avatar:

```python
# Option 1: In Cell 8, update:
TEST_AVATAR_PATH = "./outputs/your_face.jpg"

# Option 2: Use Cell 9 for custom testing
```

## 🚀 Next Steps

1. **Test with real avatar** - Upload your face image
2. **Integrate Ollama** - Connect Llama 3.2 3b (optional)
3. **Deploy as API** - Use FastAPI for web service
4. **Add GPU support** - For faster video generation
5. **Batch processing** - Process multiple responses

## 📚 Additional Resources

- **Wav2Lip:** https://github.com/Rudrabha/Wav2Lip
- **Edge-TTS:** https://github.com/rany2/edge-tts
- **Ollama:** https://ollama.ai/

## 💡 Tips

- Use **GPU** for 5-10x faster video generation
- Keep responses **short** for better real-time feel
- Use **clear face images** for best lip-sync quality
- **Cache** frequently used responses for speed

## 🐛 Common Issues

**Issue:** "asyncio event loop already running"
**Solution:** Restart the notebook kernel

**Issue:** Video generation takes too long
**Solution:** Use GPU or lower resolution

**Issue:** Audio not playing in notebook
**Solution:** Check browser audio permissions

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure Wav2Lip is set up properly
4. Check the notebook cell outputs for error messages

## 📄 License

This is a testing module. Check individual component licenses:
- Wav2Lip: Research purposes only
- Edge-TTS: Open source
- Your implementation: As per your requirements

---

**Created for:** Testing talking avatar chatbot functionality  
**Python Version:** 3.12.3  
**Platform:** Windows  
**Date:** January 2026

