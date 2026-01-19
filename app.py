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
        "what is ai": """Artificial Intelligence, commonly known as AI, is a branch of computer science 
        that focuses on creating intelligent machines capable of performing tasks that typically require 
        human intelligence. These tasks include learning from experience, understanding natural language, 
        recognizing patterns, solving problems, and making decisions.""",
        
        "what is machine learning": """Machine Learning is a subset of artificial intelligence that enables 
        computers to learn and improve from experience without being explicitly programmed. It focuses on 
        developing algorithms that can analyze data, identify patterns, and make decisions with minimal 
        human intervention.""",
        
        "hello": """Hello! I'm Aria, your AI assistant. I'm here to help answer your questions and provide 
        information on a wide range of topics. Feel free to ask me anything!""",
        
        "who are you": """I'm Aria, an AI-powered virtual assistant. I can answer questions, provide information, 
        and help you with various topics.""",
        
        "how are you": """I'm doing great, thank you for asking! I'm always ready and excited to help answer 
        your questions. How can I help you today?""",
    }
    
    question_lower = question.lower().strip()
    response = None
    for key, value in responses.items():
        if key in question_lower:
            response = ' '.join(value.split())
            break
    
    if response is None:
        response = """That's an interesting question! I can help you with questions about artificial intelligence, 
        machine learning, and technology. Feel free to ask me about these topics!"""
    
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


def text_to_audio_pyttsx3(text: str, output_path: str):
    """Convert text to audio using pyttsx3 (offline)."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()


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
    if not WAV2LIP_PATH.exists() or not WAV2LIP_CHECKPOINT.exists():
        print("⚠️ Wav2Lip not configured, skipping video generation")
        return False
    
    # Create temp directory for Wav2Lip (required for audio processing)
    temp_dir = WAV2LIP_PATH / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    inference_script = WAV2LIP_PATH / "inference.py"
    
    # Force GPU usage
    cmd = [
        sys.executable,
        str(inference_script),
        "--checkpoint_path", str(WAV2LIP_CHECKPOINT),
        "--face", avatar_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--pads", "0", "10", "0", "0",
        "--nosmooth"  # Faster processing
    ]
    
    # Set environment to force GPU usage
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '0'
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # Reduced timeout for GPU
            env=env
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Video generation error: {e}")
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

