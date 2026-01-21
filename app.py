"""
Talking Avatar Web App with Streaming Responses

To Run:
1. Install: pip install -r requirements.txt
2. Run: python app.py
3. Open: http://localhost:5000

Features:
- Multi-region TTS support (Edge TTS, Google TTS, Offline TTS)
- Automatic fallback for blocked regions
- Streaming responses
- Wav2Lip integration
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file
import os
import sys
import time
import asyncio
import subprocess
import json
from pathlib import Path
from typing import Generator
import threading
import cv2
import numpy as np
from queue import Queue
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# Import TTS libraries with fallback support
TTS_ENGINE = None
try:
    import edge_tts
    TTS_ENGINE = "edge"
    print("✓ Edge TTS loaded")
except ImportError:
    print("⚠ Edge TTS not available")

if TTS_ENGINE is None:
    try:
        from gtts import gTTS
        TTS_ENGINE = "gtts"
        print("✓ Google TTS loaded")
    except ImportError:
        print("⚠ Google TTS not available")

if TTS_ENGINE is None:
    try:
        import pyttsx3
        TTS_ENGINE = "pyttsx3"
        print("✓ Offline TTS loaded")
    except ImportError:
        print("⚠ No TTS engine available!")


TTS_ENGINE = "pyttsx3"
app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path("./outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

WAV2LIP_PATH = Path("./Wav2Lip")
WAV2LIP_CHECKPOINT = WAV2LIP_PATH / "checkpoints" / "wav2lip_gan.pth"

# Avatar cache
# You can set this to your custom avatar path
AVATAR_IMAGE_PATH = Path("/chatbot/app_code/ai_avatar_chatbot/outputs/avatar.jpg")

# Fallback to local path if custom path doesn't exist
if not AVATAR_IMAGE_PATH.exists():
    AVATAR_IMAGE_PATH = OUTPUT_DIR / "avatar.jpg"
    print(f"⚠️ Custom avatar not found, using fallback: {AVATAR_IMAGE_PATH}")
else:
    print(f"✅ Using custom avatar: {AVATAR_IMAGE_PATH}")

# Response queue for streaming
response_queues = {}


def create_avatar_image():
    """Create a simple avatar image if it doesn't exist."""
    if not AVATAR_IMAGE_PATH.exists():
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        # Create a nice gradient background
        for y in range(512):
            for x in range(512):
                img[y, x] = (100 + y // 4, 150 + x // 4, 200)
        
        # Add circle for face
        center = (256, 256)
        cv2.circle(img, center, 150, (255, 220, 180), -1)
        cv2.circle(img, center, 150, (200, 180, 150), 3)
        
        # Add eyes
        cv2.circle(img, (206, 230), 15, (50, 50, 50), -1)
        cv2.circle(img, (306, 230), 15, (50, 50, 50), -1)
        
        # Add smile
        cv2.ellipse(img, (256, 280), (60, 40), 0, 0, 180, (200, 100, 100), 3)
        
        cv2.imwrite(str(AVATAR_IMAGE_PATH), img)
    return str(AVATAR_IMAGE_PATH)


def hardcoded_chatbot(question: str) -> Generator[str, None, None]:
    """Generate response for the question word by word for streaming."""

    responses = {
        "hello": "Hello! How can I help you today?",

        "hi": "Hi there! Hope you are doing well.",

        "hey": "Hey! Nice to see you. What can I do for you?",


        "what is fever": "Fever is an increase in body temperature above normal. It usually happens when the body is fighting an infection. Fever helps the immune system work better.",

        "what is headache": "A headache is pain or pressure felt in the head or neck. It can be caused by stress, lack of sleep, dehydration, or illness.",

        "what is cough": "A cough is a reflex action that helps clear the airways. It can be caused by infections, allergies, or irritation in the throat.",

        "what is cold": "The common cold is a viral infection of the nose and throat. Symptoms include sneezing, runny nose, sore throat, and mild fever.",
        "what is fever explain": "Fever is a temporary increase in body temperature above the normal level of about 37°C (98.6°F). It usually occurs when the body is fighting an infection caused by viruses, bacteria, or other germs. Fever is part of the body’s natural defense mechanism and helps the immune system work more effectively. When body temperature rises, it becomes harder for harmful microorganisms to survive. Fever can also be caused by inflammation, heat exhaustion, or certain medications. Common symptoms along with fever include sweating, chills, headache, weakness, and body aches. Mild fever is usually not dangerous, but very high or long-lasting fever may require medical attention.",
          
        "what is headache explain": "A headache is pain, discomfort, or pressure felt in the head, scalp, or neck region. It is one of the most common health problems and can affect people of all ages. Headaches can be caused by stress, lack of sleep, dehydration, eye strain, illness, or changes in routine. There are different types of headaches, such as tension headaches, migraines, and sinus headaches. The pain may feel dull, sharp, throbbing, or tight depending on the type. Most headaches are not serious and improve with rest, hydration, and pain relief, but frequent or severe headaches may need medical evaluation.",
          
        "what is cough explain": "A cough is a natural reflex action that helps clear the airways of mucus, dust, smoke, or other irritants. It plays an important role in protecting the lungs and keeping the breathing passages clean. Cough can be caused by infections like the common cold or flu, allergies, asthma, smoking, or throat irritation. There are different types of coughs, such as dry cough and productive cough that brings out mucus. Cough may be temporary or long-lasting depending on the cause. While mild cough usually resolves on its own, persistent or severe cough may indicate an underlying health condition.",
          
        "what is cold explain": "The common cold is a viral infection that affects the nose, throat, and upper respiratory tract. It is caused by different viruses and spreads easily from person to person through air droplets or contact. Common symptoms include sneezing, runny or blocked nose, sore throat, cough, mild fever, and tiredness. The cold is usually not serious and most people recover within a few days to a week. There is no specific cure for the common cold, but rest, fluids, and basic medicines can help relieve symptoms. Good hygiene helps prevent its spread.",

        
        "default": "This is a sample response from the chatbot."
    }
    
    question_lower = question.lower().strip()
    response = None
    for key, value in responses.items():
        if key in question_lower:
            response = ' '.join(value.split())
            break
    
    if response is None:
        response = """llm is not working!"""
    
    # Stream response word by word (3-4 words at a time for natural feel)
    words = response.split()
    chunk_size = 3
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        yield chunk + ' '
        time.sleep(0.05)  # Small delay for natural streaming feel


# Removed - now using direct generator from hardcoded_chatbot

async def text_to_audio_edge_async(text: str, output_path: str, voice: str = "en-US-AriaNeural"):
    """Convert text to audio using Edge TTS."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def text_to_audio_gtts(text: str, output_path: str):
    """Convert text to audio using Google TTS."""
    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)


# def text_to_audio_pyttsx3(text: str, output_path: str):
#     """Convert text to audio using pyttsx3 (offline)."""
#     import pyttsx3
#     import time
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')
#     if voices:
#         engine.setProperty('voice', voices[0].id)
#     engine.save_to_file(text, output_path)
#     engine.runAndWait()
#     time.sleep(0.2)  # Ensure file is written
#     import os
#     if not os.path.exists(output_path):
#         raise Exception(f"Failed to create audio file: {output_path}")
def text_to_audio_pyttsx3(text: str, output_path: str):
    """Convert text to audio using pyttsx3 with optimized male English voice."""
    import pyttsx3
    import time

    # Initialize the TTS engine
    engine = pyttsx3.init()

    # Get available voices
    voices = engine.getProperty('voices')

    # Set a male English voice — adjust index if you prefer a different one
    # e.g., voices[17] for "english-us", voices[15] for "english_rp", etc.
    voice_index = 17  # english-us
    if len(voices) > voice_index:
        engine.setProperty('voice', voices[voice_index].id)

    # Set speaking rate (words per minute)
    engine.setProperty('rate', 150)  # a more natural speaking rate

    # Set volume (0.0 to 1.0)
    engine.setProperty('volume', 0.9)

    # Save speech to audio file
    engine.save_to_file(text, output_path)

    # Run engine to process and save file
    engine.runAndWait()

    # Slight pause to ensure file finishes writing
    time.sleep(0.3)


def text_to_audio(text: str, output_path: str):
    """
    Convert text to audio with automatic fallback support.
    Tries Edge TTS first, then Google TTS, then offline TTS.
    """
    global TTS_ENGINE
    
    # Try Edge TTS first (if available or if we think it's available)
    if TTS_ENGINE == "edge" or TTS_ENGINE is None:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(text_to_audio_edge_async(text, output_path))
                TTS_ENGINE = "edge"  # Confirm it works
                return
            finally:
                loop.close()
        except Exception as e:
            print(f"  ⚠ Edge TTS failed: {str(e)[:80]}")
            TTS_ENGINE = "gtts"  # Switch to fallback
    
    # Try Google TTS
    if TTS_ENGINE == "gtts":
        try:
            text_to_audio_gtts(text, output_path)
            return
        except Exception as e:
            print(f"  ⚠ Google TTS failed: {str(e)[:80]}")
            TTS_ENGINE = "pyttsx3"  # Switch to last resort
    
    # Last resort: offline TTS
    if TTS_ENGINE == "pyttsx3":
        try:
            text_to_audio_pyttsx3(text, output_path)
            return
        except Exception as e:
            print(f"  ✗ All TTS engines failed: {str(e)[:80]}")
            raise Exception("No TTS engine available")


def generate_video(audio_path: str, output_path: str, avatar_path: str):
    """Generate lip-synced video using Wav2Lip with GPU acceleration."""
    print(f"\n{'='*70}")
    print(f"VIDEO GENERATION - DEBUG")
    print(f"{'='*70}")
    
    # Check Wav2Lip
    print(f"1. Checking Wav2Lip setup...")
    if not WAV2LIP_PATH.exists():
        print(f"   ✗ Wav2Lip path not found: {WAV2LIP_PATH}")
        return False
    print(f"   ✓ Wav2Lip path: {WAV2LIP_PATH}")
    
    if not WAV2LIP_CHECKPOINT.exists():
        print(f"   ✗ Checkpoint not found: {WAV2LIP_CHECKPOINT}")
        return False
    print(f"   ✓ Checkpoint: {WAV2LIP_CHECKPOINT}")
    
    # Check inference script
    inference_script = WAV2LIP_PATH / "inference.py"
    if not inference_script.exists():
        print(f"   ✗ Inference script not found: {inference_script}")
        return False
    print(f"   ✓ Inference script: {inference_script}")
    
    # Check inputs
    print(f"\n2. Checking input files...")
    if not os.path.exists(audio_path):
        print(f"   ✗ Audio not found: {audio_path}")
        return False
    audio_size = os.path.getsize(audio_path)
    print(f"   ✓ Audio: {audio_path} ({audio_size} bytes)")
    
    if not os.path.exists(avatar_path):
        print(f"   ✗ Avatar not found: {avatar_path}")
        return False
    avatar_size = os.path.getsize(avatar_path)
    print(f"   ✓ Avatar: {avatar_path} ({avatar_size} bytes)")
    
    # Create temp directory
    print(f"\n3. Creating temp directory...")
    temp_dir = WAV2LIP_PATH / "temp"
    temp_dir.mkdir(exist_ok=True)
    print(f"   ✓ Temp dir: {temp_dir}")
    
    # Build command with absolute paths
    print(f"\n4. Building command...")
    
    # Convert all paths to absolute
    abs_checkpoint = os.path.abspath(str(WAV2LIP_CHECKPOINT))
    abs_avatar = os.path.abspath(avatar_path)
    abs_audio = os.path.abspath(audio_path)
    abs_output = os.path.abspath(output_path)
    
    cmd = [
        sys.executable,
        "inference.py",  # Relative to Wav2Lip directory
        "--checkpoint_path", abs_checkpoint,
        "--face", abs_avatar,
        "--audio", abs_audio,
        "--outfile", abs_output,
        "--pads", "0", "10", "0", "0",
        "--nosmooth"
    ]
    print(f"   Working dir: {WAV2LIP_PATH}")
    print(f"   Command: {' '.join(cmd)}")
    
    # Set environment
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'
    print(f"   GPU Device: {env['CUDA_VISIBLE_DEVICES']}")
    
    # Run Wav2Lip
    print(f"\n5. Running Wav2Lip (timeout: 30s)...")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            env=env,
            cwd=str(WAV2LIP_PATH)  # Run from Wav2Lip directory
        )
        
        print(f"\n6. Process completed")
        print(f"   Return code: {result.returncode}")
        
        if result.stdout:
            print(f"\n   STDOUT:")
            for line in result.stdout.split('\n')[:20]:  # First 20 lines
                print(f"   {line}")
        
        if result.stderr:
            print(f"\n   STDERR:")
            for line in result.stderr.split('\n')[:20]:  # First 20 lines
                print(f"   {line}")
        
        # Check output
        print(f"\n7. Checking output...")
        if os.path.exists(output_path):
            out_size = os.path.getsize(output_path)
            print(f"   ✓ Output created: {output_path} ({out_size} bytes)")
            if out_size > 1000:
                print(f"   ✓ SUCCESS - Video generated")
                print(f"{'='*70}\n")
                return True
            else:
                print(f"   ✗ FAILED - File too small (corrupted)")
                print(f"{'='*70}\n")
                return False
        else:
            print(f"   ✗ FAILED - Output file not created")
            print(f"{'='*70}\n")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n✗ TIMEOUT - Process took >30s")
        print(f"{'='*70}\n")
        return False
    except Exception as e:
        print(f"\n✗ EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        return False


def process_video_async(session_id: str, text: str, avatar_path: str):
    """Process video generation in background thread with GPU acceleration."""
    try:
        import torch
        
        # Ensure GPU is available
        if torch.cuda.is_available():
            torch.cuda.set_device(0)  # Use first GPU
            print(f"🎮 Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️ GPU not available, using CPU")
        
        start_time = time.time()
        
        # Generate audio (fast)
        audio_path = OUTPUT_DIR / f"audio_{session_id}.mp3"
        text_to_audio(text, str(audio_path))
        audio_time = time.time() - start_time
        print(f"✓ Audio generated in {audio_time:.2f}s")
        
        # Generate video with GPU (should be fast with RTX 3090)
        video_start = time.time()
        video_path = OUTPUT_DIR / f"video_{session_id}.mp4"
        success = generate_video(str(audio_path), str(video_path), avatar_path)
        video_time = time.time() - video_start
        
        if success:
            total_time = time.time() - start_time
            print(f"✓ Video generated in {video_time:.2f}s (total: {total_time:.2f}s)")
            
            if session_id in response_queues:
                response_queues[session_id].put({
                    "type": "video_ready",
                    "video_url": f"/video/{session_id}"
                })
        else:
            print("✗ Video generation failed")
            if session_id in response_queues:
                response_queues[session_id].put({
                    "type": "error",
                    "message": "Video generation failed"
                })
                
    except Exception as e:
        print(f"✗ Error in video processing: {e}")
        import traceback
        traceback.print_exc()
        if session_id in response_queues:
            response_queues[session_id].put({
                "type": "error",
                "message": str(e)
            })


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Handle user questions with streaming response."""
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    session_id = str(int(time.time() * 1000))
    
    def generate():
        try:
            # Use the configured avatar
            if not AVATAR_IMAGE_PATH.exists():
                avatar_path = create_avatar_image()
            else:
                avatar_path = str(AVATAR_IMAGE_PATH)
            
            # Start collecting full text for audio/video
            full_text_parts = []
            response_queues[session_id] = Queue()
            
            # Send session ID immediately
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
            
            # Stream text word by word from generator
            for chunk in hardcoded_chatbot(question):
                full_text_parts.append(chunk)
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
            
            # Get full text
            full_text = ''.join(full_text_parts).strip()
            
            # Signal text complete
            yield f"data: {json.dumps({'type': 'text_complete', 'full_text': full_text})}\n\n"
            
            # Start video generation in background (non-blocking)
            thread = threading.Thread(
                target=process_video_async,
                args=(session_id, full_text, avatar_path)
            )
            thread.daemon = True
            thread.start()
            
            # Wait for video with reduced timeout (GPU is faster)
            start_time = time.time()
            timeout = 15  # Reduced from 45s for GPU
            
            while time.time() - start_time < timeout:
                if not response_queues[session_id].empty():
                    result = response_queues[session_id].get()
                    yield f"data: {json.dumps(result)}\n\n"
                    break
                time.sleep(0.2)  # Check more frequently
            else:
                yield f"data: {json.dumps({'type': 'timeout', 'message': 'Video generation timeout'})}\n\n"
            
            # Cleanup
            if session_id in response_queues:
                del response_queues[session_id]
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/video/<session_id>')
def get_video(session_id):
    """Serve generated video."""
    video_path = OUTPUT_DIR / f"video_{session_id}.mp4"
    
    if video_path.exists():
        return send_file(video_path, mimetype='video/mp4')
    else:
        return jsonify({"error": "Video not found"}), 404


@app.route('/audio/<session_id>')
def get_audio(session_id):
    """Serve generated audio."""
    audio_path = OUTPUT_DIR / f"audio_{session_id}.mp3"
    
    if audio_path.exists():
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        return jsonify({"error": "Audio not found"}), 404


@app.route('/avatar')
def get_avatar():
    """Serve the avatar image."""
    if AVATAR_IMAGE_PATH.exists():
        return send_file(AVATAR_IMAGE_PATH, mimetype='image/jpeg')
    else:
        # Return a 404 if avatar doesn't exist
        return jsonify({"error": "Avatar not found"}), 404


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "wav2lip_available": WAV2LIP_PATH.exists() and WAV2LIP_CHECKPOINT.exists(),
        "avatar_available": AVATAR_IMAGE_PATH.exists(),
        "avatar_path": str(AVATAR_IMAGE_PATH)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Talking Avatar Web App")
    print("="*60)
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            print(f"   ✅ GPU acceleration ENABLED")
            # Warm up GPU
            torch.cuda.set_device(0)
        else:
            print("⚠️  No GPU detected - will run on CPU (slower)")
    except Exception as e:
        print(f"⚠️  GPU check failed: {e}")
    
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    
    if AVATAR_IMAGE_PATH.exists():
        print(f"🎭 Avatar: {AVATAR_IMAGE_PATH.absolute()}")
        print(f"   ✅ Custom avatar loaded")
    else:
        print(f"🎭 Avatar: Creating fallback avatar...")
        create_avatar_image()
        print(f"   ⚠️ Using fallback avatar at: {AVATAR_IMAGE_PATH}")
    
    # Check TTS Engine
    if TTS_ENGINE:
        engine_names = {
            "edge": "Edge TTS (Microsoft)",
            "gtts": "Google TTS",
            "pyttsx3": "Offline TTS"
        }
        print(f"🔊 TTS Engine: {engine_names.get(TTS_ENGINE, TTS_ENGINE)} (auto-fallback enabled)")
    else:
        print("⚠️  TTS: No engine available - install edge-tts, gtts, or pyttsx3")
    
    if WAV2LIP_PATH.exists() and WAV2LIP_CHECKPOINT.exists():
        print("✅ Wav2Lip: Ready (GPU accelerated)")
    else:
        print("⚠️  Wav2Lip: Not configured (audio-only mode)")
    
    print("\n🌐 Server starting at: http://localhost:5000")
    print("⚡ Optimizations:")
    print("   - Streaming response (3-4 words at a time)")
    print("   - GPU acceleration for video generation")
    print("   - Parallel audio/video processing")
    print("="*60 + "\n")
    
    # Set environment for GPU
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

