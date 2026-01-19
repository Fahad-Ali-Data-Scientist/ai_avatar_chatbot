# Fix Wav2Lip "temp/temp.wav" Error

## The Problem

You're getting this error:
```
Error opening output temp/temp.wav: No such file or directory
FileNotFoundError: [Errno 2] No such file or directory: 'temp/temp.wav'
```

**Cause:** Wav2Lip tries to create temporary audio files in a `temp/` directory, but this directory doesn't exist.

## ✅ Quick Fix (2 Methods)

### Method 1: Manual Fix (30 seconds)

**Step 1:** Create the temp directory manually

```bash
# Navigate to your Wav2Lip folder
cd Wav2Lip

# Create temp directory
mkdir temp

# Or if you're in the project root:
mkdir -p Wav2Lip/temp
```

**Step 2:** Run your code again - it should work now!

### Method 2: Update the Code (Automatic Fix)

Update the `LipSyncGenerator` class in your notebook to automatically create the temp directory.

**Find this code in Cell 10 (Lip-Sync Module):**

```python
class LipSyncGenerator:
    def __init__(self, wav2lip_path: str = "./Wav2Lip"):
        """
        Initialize Lip-sync generator.
        
        Args:
            wav2lip_path: Path to Wav2Lip repository
        """
        self.wav2lip_path = Path(wav2lip_path)
        self.checkpoint_path = self.wav2lip_path / "checkpoints" / "wav2lip_gan.pth"
        
        if not self.wav2lip_path.exists():
            raise FileNotFoundError(f"Wav2Lip not found at {self.wav2lip_path}")
        
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at {self.checkpoint_path}")
        
        print(f"✓ Lip-sync generator initialized")
```

**Replace with this:**

```python
class LipSyncGenerator:
    def __init__(self, wav2lip_path: str = "./Wav2Lip"):
        """
        Initialize Lip-sync generator.
        
        Args:
            wav2lip_path: Path to Wav2Lip repository
        """
        self.wav2lip_path = Path(wav2lip_path)
        self.checkpoint_path = self.wav2lip_path / "checkpoints" / "wav2lip_gan.pth"
        
        if not self.wav2lip_path.exists():
            raise FileNotFoundError(f"Wav2Lip not found at {self.wav2lip_path}")
        
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at {self.checkpoint_path}")
        
        # ✅ FIX: Create temp directory for Wav2Lip
        temp_dir = self.wav2lip_path / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        print(f"✓ Lip-sync generator initialized")
        print(f"  Temp directory created: {temp_dir}")
```

**Then, also update the `generate_talking_video` method in the same class:**

Find this part:
```python
def generate_talking_video(
    self, 
    face_image_path: str, 
    audio_path: str, 
    output_path: str,
    quality: str = "high"
):
    """
    Generate lip-synced video from face image and audio.
    
    Args:
        face_image_path: Path to face image
        audio_path: Path to audio file
        output_path: Path to save output video
        quality: Quality setting ('high' or 'fast')
    """
    inference_script = self.wav2lip_path / "inference.py"
```

Add these lines right after the docstring:
```python
def generate_talking_video(
    self, 
    face_image_path: str, 
    audio_path: str, 
    output_path: str,
    quality: str = "high"
):
    """
    Generate lip-synced video from face image and audio.
    
    Args:
        face_image_path: Path to face image
        audio_path: Path to audio file
        output_path: Path to save output video
        quality: Quality setting ('high' or 'fast')
    """
    # ✅ FIX: Ensure temp directory exists
    temp_dir = self.wav2lip_path / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    inference_script = self.wav2lip_path / "inference.py"
```

## 🔍 Why This Happens

Wav2Lip's audio processing module (`audio.py`) creates temporary WAV files in a `temp/` folder for audio format conversion. If this folder doesn't exist, it crashes.

This is a known issue with Wav2Lip - it doesn't automatically create the temp directory.

## ✅ Verify the Fix

After applying one of the fixes above:

1. **Check the directory exists:**
   ```bash
   ls -la Wav2Lip/temp
   # Should show an empty directory
   ```

2. **Run your code again:**
   ```python
   result = complete_talking_avatar_pipeline(
       question="what is ai",
       avatar_image_path=str(sample_avatar_path),
       use_ollama=False,
       tts_voice="en-US-AriaNeural"
   )
   ```

3. **Expected output:**
   ```
   ✓ Lip-sync generator initialized
     Temp directory created: Wav2Lip/temp
   
   [3/4] Generating lip-synced video...
   Generating lip-synced video...
   Face: outputs/sample_avatar.jpg
   Audio: outputs/response_audio.mp3
   Output: outputs/talking_avatar.mp4
   ✓ Video generated successfully: outputs/talking_avatar.mp4
   ```

## 📝 Summary

**Problem:** Missing `temp/` directory  
**Solution:** Create `mkdir Wav2Lip/temp` OR update the code to create it automatically  
**Time:** 30 seconds  

---

## 🆘 Still Having Issues?

### Issue: Permission denied when creating temp directory

**Solution:**
```bash
# Make sure you have write permissions
chmod 755 Wav2Lip
mkdir Wav2Lip/temp
```

### Issue: Wav2Lip creates other temporary files

**Solution:** The temp directory fix handles most cases, but if Wav2Lip creates other temp files in different locations, you might need to:

```python
# Create additional temp directories
(self.wav2lip_path / "results").mkdir(exist_ok=True)
(self.wav2lip_path / "checkpoints").mkdir(exist_ok=True)
```

### Issue: Still getting "System error"

**Possible causes:**
1. Audio file is corrupted - Regenerate it with TTS
2. Audio file format is wrong - Should be MP3
3. Disk space is full - Check with `df -h`
4. Path has special characters - Use simple paths

---

**Quick Command to Fix Everything:**

```bash
# Run this from your project root
cd talking_avatar_test
mkdir -p Wav2Lip/temp
mkdir -p Wav2Lip/results
chmod -R 755 Wav2Lip
```

Then run your notebook again!

---

✅ **Result:** Your Wav2Lip should now work without the temp directory error!
