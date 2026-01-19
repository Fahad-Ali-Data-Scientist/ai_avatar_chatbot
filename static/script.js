// Elements
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const responseText = document.getElementById('responseText');
const responseContainer = document.getElementById('responseContainer');
const avatarImage = document.getElementById('avatarImage');
const avatarVideo = document.getElementById('avatarVideo');
const audioPlayer = document.getElementById('audioPlayer');
const loadingRing = document.getElementById('loadingRing');
const statusIndicator = document.getElementById('statusIndicator');
const suggestions = document.querySelectorAll('.suggestion-btn');
const avatarSubtitle = document.getElementById('avatarSubtitle');

// State
let isProcessing = false;
let currentSessionId = null;

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    // Load avatar image
    loadAvatarImage();
    
    // Setup event listeners
    sendBtn.addEventListener('click', handleSend);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) {
            handleSend();
        }
    });
    
    // Suggestion buttons
    suggestions.forEach(btn => {
        btn.addEventListener('click', () => {
            questionInput.value = btn.dataset.question;
            handleSend();
        });
    });
    
    // Mic button (placeholder)
    micBtn.addEventListener('click', () => {
        alert('Voice input feature coming soon!');
    });
    
    // Focus input
    questionInput.focus();
});

// Load avatar image
function loadAvatarImage() {
    // Load the actual avatar image from server
    avatarImage.src = '/avatar?t=' + new Date().getTime(); // Add timestamp to prevent caching
    
    avatarImage.onerror = function() {
        // If avatar image fails to load, create a placeholder
        console.warn('Avatar image not found, creating placeholder');
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        // Gradient background
        const gradient = ctx.createLinearGradient(0, 0, 512, 512);
            gradient.addColorStop(0, '#f5d5b8');
            gradient.addColorStop(1, '#e8c4a0');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 512, 512);
            
            // Face circle
            ctx.fillStyle = '#ffdbac';
            ctx.beginPath();
            ctx.arc(256, 256, 150, 0, Math.PI * 2);
            ctx.fill();
            
            // Eyes
            ctx.fillStyle = '#333';
            ctx.beginPath();
            ctx.arc(206, 230, 15, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(306, 230, 15, 0, Math.PI * 2);
            ctx.fill();
            
            // Smile
            ctx.strokeStyle = '#c87a6a';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.arc(256, 260, 50, 0.2, Math.PI - 0.2);
            ctx.stroke();
            
            avatarImage.src = canvas.toDataURL();
    };
    
    avatarImage.onload = function() {
        console.log('✅ Avatar image loaded successfully');
        // Show the avatar
        avatarImage.style.display = 'block';
    };
}

// Handle send
async function handleSend() {
    const question = questionInput.value.trim();
    
    if (!question || isProcessing) return;
    
    isProcessing = true;
    sendBtn.disabled = true;
    questionInput.disabled = true;
    
    // Clear previous response
    responseText.textContent = '';
    responseText.classList.add('typing');
    
    // Show loading
    loadingRing.classList.add('active');
    statusIndicator.classList.add('speaking');
    
    // Hide video, show image
    avatarVideo.classList.remove('active');
    avatarImage.style.display = 'block';
    
    try {
        await streamResponse(question);
    } catch (error) {
        console.error('Error:', error);
        responseText.textContent = 'Sorry, an error occurred. Please try again.';
        responseText.classList.remove('typing');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        questionInput.disabled = false;
        questionInput.value = '';
        questionInput.focus();
        loadingRing.classList.remove('active');
    }
}

// Stream response from server
async function streamResponse(question) {
    const response = await fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';
    
    while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete messages
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                switch (data.type) {
                    case 'text':
                        responseText.textContent += data.content;
                        fullText += data.content;
                        // Auto scroll
                        responseContainer.scrollTop = responseContainer.scrollHeight;
                        break;
                        
                    case 'text_complete':
                        responseText.classList.remove('typing');
                        fullText = data.full_text;
                        break;
                        
                    case 'session_id':
                        currentSessionId = data.session_id;
                        // Show loading state
                        loadingRing.classList.add('active');
                        avatarSubtitle.textContent = 'Generating video...';
                        break;
                        
                    case 'video_ready':
                        loadingRing.classList.remove('active');
                        await playVideo(data.video_url);
                        break;
                        
                    case 'timeout':
                        console.log('⏱️ Video generation timeout, playing audio only');
                        loadingRing.classList.remove('active');
                        avatarSubtitle.textContent = 'Playing audio...';
                        statusIndicator.classList.remove('speaking');
                        // Try to play audio if available
                        if (currentSessionId) {
                            tryPlayAudio(currentSessionId);
                        }
                        break;
                        
                    case 'error':
                        console.error('❌ Server error:', data.message);
                        loadingRing.classList.remove('active');
                        avatarSubtitle.textContent = 'Error occurred';
                        statusIndicator.classList.remove('speaking');
                        setTimeout(() => {
                            avatarSubtitle.textContent = 'Ask me anything';
                        }, 3000);
                        break;
                }
            }
        }
    }
}

// Play generated video
async function playVideo(videoUrl) {
    try {
        console.log('🎬 Loading video:', videoUrl);
        avatarSubtitle.textContent = 'Loading video...';
        
        // Set video source with cache buster
        avatarVideo.src = videoUrl + '?t=' + new Date().getTime();
        
        // Hide image, show video
        avatarImage.classList.add('hidden');
        avatarVideo.classList.add('active');
        
        // Wait for video to load
        await new Promise((resolve, reject) => {
            avatarVideo.onloadeddata = () => {
                console.log('✅ Video loaded successfully');
                resolve();
            };
            avatarVideo.onerror = (e) => {
                console.error('❌ Video load error:', e);
                reject(e);
            };
            
            // Timeout after 10 seconds
            setTimeout(() => reject(new Error('Video load timeout')), 10000);
        });
        
        avatarSubtitle.textContent = 'Speaking...';
        statusIndicator.classList.add('speaking');
        
        // Play video with audio
        await avatarVideo.play();
        console.log('▶️ Video playing with lip-sync');
        
        // When video ends, show image again
        avatarVideo.onended = () => {
            console.log('✅ Video playback complete');
            avatarVideo.classList.remove('active');
            avatarImage.classList.remove('hidden');
            statusIndicator.classList.remove('speaking');
            avatarSubtitle.textContent = 'Ask me anything';
            
            // Clear video source to free memory
            avatarVideo.src = '';
        };
        
    } catch (error) {
        console.error('❌ Error playing video:', error);
        avatarVideo.classList.remove('active');
        avatarImage.classList.remove('hidden');
        statusIndicator.classList.remove('speaking');
        avatarSubtitle.textContent = 'Playing audio only...';
        
        // Fallback to audio only
        if (currentSessionId) {
            tryPlayAudio(currentSessionId);
        }
    }
}

// Try to play audio
function tryPlayAudio(sessionId) {
    const audioUrl = `/audio/${sessionId}`;
    audioPlayer.src = audioUrl;
    audioPlayer.play().catch(err => {
        console.log('Audio playback failed:', err);
    });
    
    audioPlayer.onplay = () => {
        statusIndicator.classList.add('speaking');
    };
    
    audioPlayer.onended = () => {
        statusIndicator.classList.remove('speaking');
    };
}

// Smooth scroll to response
function scrollToResponse() {
    responseContainer.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

// Handle visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause video/audio when tab is hidden
        if (avatarVideo.classList.contains('active')) {
            avatarVideo.pause();
        }
        audioPlayer.pause();
    }
});

// Add some visual feedback on input
questionInput.addEventListener('input', () => {
    if (questionInput.value.trim()) {
        sendBtn.style.opacity = '1';
    } else {
        sendBtn.style.opacity = '0.7';
    }
});

