// Text to Speech functionality
document.addEventListener('DOMContentLoaded', function() {
    const ttsInput = document.getElementById('tts-input');
    const charCount = document.getElementById('char-count');
    const generateBtn = document.getElementById('generate-speech-btn');
    const voiceSelect = document.getElementById('voice-select');
    const speedRange = document.getElementById('speed-range');
    const speedValue = document.getElementById('speed-value');
    const previewSection = document.querySelector('.tts-preview-section');
    const audioPreview = document.getElementById('audio-preview');
    const downloadBtn = document.getElementById('download-audio-btn');
    const copyUrlBtn = document.getElementById('copy-url-btn');

    // Update character count
    ttsInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });

    // Update speed display
    speedRange.addEventListener('input', function() {
        speedValue.textContent = `${this.value}x`;
    });

    // Generate speech
    generateBtn.addEventListener('click', async function() {
        const text = ttsInput.value.trim();
        if (!text) {
            alert('Please enter some text to convert to speech.');
            return;
        }

        generateBtn.disabled = true;
        generateBtn.innerHTML = '<svg class="spinner" viewBox="0 0 50 50"><circle cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle></svg>Generating...';

        try {
            const response = await fetch('/api/tts/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: voiceSelect.value,
                    speed: speedRange.value
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate speech');
            }

            const data = await response.json();
            
            // Update audio player
            audioPreview.src = data.audioUrl;
            previewSection.style.display = 'block';
            
            // Update download button
            downloadBtn.onclick = () => {
                const link = document.createElement('a');
                link.href = data.audioUrl;
                link.download = 'speech.mp3';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };

            // Update copy URL button
            copyUrlBtn.onclick = () => {
                navigator.clipboard.writeText(data.audioUrl)
                    .then(() => {
                        const originalText = copyUrlBtn.innerHTML;
                        copyUrlBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Copied!';
                        setTimeout(() => {
                            copyUrlBtn.innerHTML = originalText;
                        }, 2000);
                    })
                    .catch(() => alert('Failed to copy URL'));
            };

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate speech. Please try again.');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>Generate Speech';
        }
    });
}); 