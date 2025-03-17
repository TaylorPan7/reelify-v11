document.addEventListener('DOMContentLoaded', function() {
    // Sidebar functionality
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        const navItems = sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                navItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Theme handling
    const themeOptions = document.querySelectorAll('.theme-option');
    if (themeOptions) {
        // Set theme immediately when the page loads
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // Set active state immediately
        themeOptions.forEach(option => {
            if (option.getAttribute('data-theme') === savedTheme) {
                option.classList.add('active');
            }
        });

        themeOptions.forEach(option => {
            option.addEventListener('click', function() {
                const theme = this.getAttribute('data-theme');
                document.documentElement.setAttribute('data-theme', theme);
                
                // Remove active class from all options
                themeOptions.forEach(opt => opt.classList.remove('active'));
                // Add active class only to clicked option
                this.classList.add('active');
                
                // Save theme preference
                localStorage.setItem('theme', theme);
            });
        });
    }

    // Fade-in animation for home page sections
    const fadeElements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });

    fadeElements.forEach(element => {
        observer.observe(element);
    });

    // Advanced Settings Toggle - Video Generator
    const toggleSettingsBtn = document.getElementById('toggle-settings');
    if (toggleSettingsBtn) {
        const settingsContent = document.getElementById('settings-content');
        toggleSettingsBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            settingsContent.classList.toggle('active');
            if (settingsContent.classList.contains('active')) {
                settingsContent.style.display = 'grid';
            } else {
                settingsContent.style.display = 'none';
            }
        });
    }

    // Advanced Settings Toggle - Image Generator
    const toggleImageSettingsBtn = document.getElementById('toggle-image-settings');
    if (toggleImageSettingsBtn) {
        const imageSettingsContent = document.getElementById('image-settings-content');
        toggleImageSettingsBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            imageSettingsContent.classList.toggle('active');
            if (imageSettingsContent.classList.contains('active')) {
                imageSettingsContent.style.display = 'grid';
            } else {
                imageSettingsContent.style.display = 'none';
            }
        });
    }

    // Advanced Settings Toggle - Captioner
    const toggleCaptionSettingsBtn = document.getElementById('toggle-caption-settings');
    if (toggleCaptionSettingsBtn) {
        const captionSettingsContent = document.getElementById('caption-settings-content');
        toggleCaptionSettingsBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            captionSettingsContent.classList.toggle('active');
            if (captionSettingsContent.classList.contains('active')) {
                captionSettingsContent.style.display = 'grid';
            } else {
                captionSettingsContent.style.display = 'none';
            }
        });
    }

    // Suggested Topics
    const topicCards = document.querySelectorAll('.topic-card');
    const topicInput = document.getElementById('topic');
    const generateBtn = document.getElementById('generate-btn');
    const progressContainer = document.querySelector('.progress-container');
    const resultContainer = document.querySelector('.result-container');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressFill = document.querySelector('.progress-fill');
    const currentStep = document.getElementById('current-step');
    const resultVideo = document.getElementById('result-video');

    if (topicCards) {
        topicCards.forEach(card => {
            card.addEventListener('click', function() {
                const topic = this.getAttribute('data-topic');
                if (topicInput) {
                    topicInput.value = topic;
                }
            });
        });
    }

    if (generateBtn && topicInput) {
        generateBtn.addEventListener('click', function() {
            const topic = topicInput.value.trim();
            if (!topic) {
                alert('Please enter a topic');
                return;
            }

            // Show progress container and hide result container
            if (progressContainer) progressContainer.style.display = 'block';
            if (resultContainer) resultContainer.style.display = 'none';

            // Reset progress UI
            if (progressText) progressText.textContent = 'Generating video...';
            if (progressPercentage) progressPercentage.textContent = '0%';
            if (progressFill) progressFill.style.width = '0%';
            if (currentStep) currentStep.textContent = 'Initializing...';

            // Start video generation
            generateVideo(topic);
        });
    }

    // Video Generator
    if (generateBtn) {
        const progressContainer = document.querySelector('.progress-container');
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressPercentage = document.getElementById('progress-percentage');
        const currentStep = document.getElementById('current-step');
        const resultContainer = document.querySelector('.result-container');
        const resultVideo = document.getElementById('result-video');
        
        // Video generation function
        function generateVideo(topic) {
            // Show loading state
            progressContainer.style.display = 'block';
            resultContainer.style.display = 'none';
            progressFill.style.width = '0%';
            progressText.textContent = 'Starting video generation...';
            progressPercentage.textContent = '0%';
            currentStep.textContent = 'Initializing...';

            // Make the API call to start video generation
            fetch('/generate-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: topic }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to start video generation');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (!data.video_id) {
                    throw new Error('No video ID received from server');
                }
                
                // Start polling for progress
                pollProgress(data.video_id);
            })
            .catch(error => {
                console.error('Error starting video generation:', error);
                progressText.textContent = 'Error starting video generation';
                currentStep.textContent = error.message || 'Failed to connect to server';
                progressFill.style.width = '0%';
                progressPercentage.textContent = '0%';
            });
        }

        // Function to poll for progress
        function pollProgress(videoId) {
            const checkProgress = () => {
                fetch(`/check-video-status/${videoId}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => {
                                throw new Error(data.error || 'Failed to check video status');
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.error) {
                            throw new Error(data.error);
                        }

                        // Update progress UI
                        const progress = data.progress || 0;
                        progressFill.style.width = `${progress}%`;
                        progressPercentage.textContent = `${progress}%`;
                        currentStep.textContent = data.current_step || 'Processing...';

                        if (data.status === 'completed') {
                            // Video is ready
                            completeVideoGeneration(data.video_url, data.srt_url);
                            return;
                        } else if (data.status === 'error') {
                            throw new Error(data.error || 'An error occurred during video generation');
                        }

                        // Continue polling
                        setTimeout(checkProgress, 2000); // Poll every 2 seconds
                    })
                    .catch(error => {
                        console.error('Error checking progress:', error);
                        progressText.textContent = 'Error generating video';
                        currentStep.textContent = error.message || 'Failed to check video status';
                        progressFill.style.width = '0%';
                        progressPercentage.textContent = '0%';
                    });
            };

            // Start polling
            checkProgress();
        }

        // Function to complete video generation
        function completeVideoGeneration(videoUrl, srtUrl) {
            progressText.textContent = 'Video generation completed!';
            progressPercentage.textContent = '100%';
            progressFill.style.width = '100%';
            
            // Show the result container
            resultContainer.style.display = 'block';
            
            // Set the video source
            resultVideo.src = videoUrl;
            resultVideo.load();
            
            // Set up download buttons
            const downloadBtn = document.getElementById('download-btn');
            const downloadSrtBtn = document.getElementById('download-srt-btn');
            
            if (downloadBtn) {
                downloadBtn.onclick = () => {
                    const link = document.createElement('a');
                    link.href = videoUrl;
                    link.download = 'generated_video.mp4';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                };
            }
            
            if (downloadSrtBtn && srtUrl) {
                downloadSrtBtn.onclick = () => {
                    const link = document.createElement('a');
                    link.href = srtUrl;
                    link.download = 'captions.srt';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                };
            }
        }
    }

    // Image Generator
    const generateImageBtn = document.getElementById('generate-image');
    if (generateImageBtn) {
        const loadingSpinner = document.getElementById('loading');
        const imageResult = document.getElementById('image-result');
        
        generateImageBtn.addEventListener('click', function() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt) {
                alert('Please enter a prompt for your image');
                return;
            }
            
            // Get advanced settings if available
            const imageStyle = document.getElementById('image-style') ? document.getElementById('image-style').value : 'realistic';
            const imageResolution = document.getElementById('image-resolution') ? document.getElementById('image-resolution').value : '1024x1024';
            
            // Show loading spinner
            loadingSpinner.style.display = 'block';
            imageResult.innerHTML = '';
            imageResult.style.display = 'none';
            
            // Simulate API call to generate image
            setTimeout(() => {
                // Hide loading spinner
                loadingSpinner.style.display = 'none';
                imageResult.style.display = 'block';
                
                // Show result
                imageResult.innerHTML = `
                    <img src="/static/sample-image.jpg" alt="Generated Image" width="100%">
                    <div class="action-buttons">
                        <button>Download Image</button>
                        <button>Share</button>
                    </div>
                `;
            }, 3000);
        });
    }

    // Captioner
    const uploadInput = document.getElementById('upload');
    if (uploadInput) {
        const uploadArea = document.querySelector('.upload-area');
        const uploadLabel = document.querySelector('.upload-label');
        const progressContainer = document.querySelector('.progress-container');
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.getElementById('caption-progress-text');
        const progressPercentage = document.getElementById('caption-progress-percentage');
        const currentStep = document.getElementById('caption-current-step');
        const resultContainer = document.querySelector('.result-container');
        
        uploadArea.addEventListener('click', function() {
            uploadInput.click();
        });
        
        uploadInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Update upload area to show selected file
                uploadLabel.textContent = this.files[0].name;
                
                // Create caption button if it doesn't exist
                let captionBtn = document.getElementById('caption-btn');
                if (!captionBtn) {
                    captionBtn = document.createElement('button');
                    captionBtn.id = 'caption-btn';
                    captionBtn.textContent = 'Generate Captions';
                    captionBtn.style.marginTop = '1rem';
                    
                    // Remove any existing button
                    const existingBtn = uploadArea.querySelector('button');
                    if (existingBtn) {
                        uploadArea.removeChild(existingBtn);
                    }
                    
                    uploadArea.appendChild(captionBtn);
                    
                    // Caption button click handler
                    captionBtn.addEventListener('click', function() {
                        // Get caption settings
                        const captionStyle = document.getElementById('caption-style') ? document.getElementById('caption-style').value : 'standard';
                        const captionPosition = document.getElementById('caption-position') ? document.getElementById('caption-position').value : 'bottom';
                        const captionLanguage = document.getElementById('caption-language') ? document.getElementById('caption-language').value : 'auto';
                        
                        // Show progress container
                        progressContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                        
                        // Reset progress
                        progressFill.style.width = '0%';
                        progressText.textContent = 'Processing video...';
                        progressPercentage.textContent = '0%';
                        currentStep.textContent = 'Initializing...';
                        
                        // Simulate caption generation
                        let progress = 0;
                        const interval = setInterval(() => {
                            progress += 10;
                            
                            if (progress <= 30) {
                                updateCaptionProgress(progress, 'Analyzing audio...');
                            } else if (progress <= 60) {
                                updateCaptionProgress(progress, 'Transcribing content...');
                            } else if (progress <= 90) {
                                updateCaptionProgress(progress, 'Generating captions...');
                            } else {
                                updateCaptionProgress(100, 'Captions generated successfully!');
                                clearInterval(interval);
                                
                                // Show result after a short delay
                                setTimeout(() => {
                                    progressContainer.style.display = 'none';
                                    resultContainer.style.display = 'block';
                                    
                                    // Set up the captions list
                                    const captionsList = document.querySelector('.captions-list');
                                    captionsList.innerHTML = `
                                        <div class="caption-item">00:00:02 - 00:00:05: This is a sample caption.</div>
                                        <div class="caption-item">00:00:06 - 00:00:09: Generated automatically by our system.</div>
                                        <div class="caption-item">00:00:10 - 00:00:14: You can download the captioned video below.</div>
                                    `;
                                    
                                    // Set the video source
                                    const captionedVideo = document.getElementById('captioned-video');
                                    if (captionedVideo) {
                                        const videoSource = captionedVideo.querySelector('source');
                                        videoSource.src = URL.createObjectURL(uploadInput.files[0]);
                                        captionedVideo.load();
                                    }
                                }, 1000);
                            }
                        }, 300);
                    });
                }
            }
        });
        
        // Helper function to update caption progress
        function updateCaptionProgress(percentage, stepText) {
            progressFill.style.width = percentage + '%';
            progressPercentage.textContent = percentage + '%';
            currentStep.textContent = stepText;
        }
        
        // Download buttons
        const downloadVideoBtn = document.getElementById('download-video-btn');
        if (downloadVideoBtn) {
            downloadVideoBtn.addEventListener('click', function() {
                alert('Download functionality will be implemented soon!');
            });
        }
        
        const downloadSrtBtn = document.getElementById('download-srt-btn');
        if (downloadSrtBtn) {
            downloadSrtBtn.addEventListener('click', function() {
                alert('SRT download functionality will be implemented soon!');
            });
        }
        
        const editCaptionsBtn = document.getElementById('edit-captions-btn');
        if (editCaptionsBtn) {
            editCaptionsBtn.addEventListener('click', function() {
                alert('Caption editing functionality will be implemented soon!');
            });
        }
    }

    // Pricing Toggle
    const billingToggle = document.getElementById('billing-toggle');
    if (billingToggle) {
        const updatePricingSavings = () => {
            const pricingContainer = document.querySelector('.pricing-container');
            const yearlyPrices = document.querySelectorAll('.price.yearly');
            const isYearly = billingToggle.checked;
            
            pricingContainer.classList.toggle('yearly', isYearly);
            yearlyPrices.forEach(price => {
                if (price.closest('.pricing-card.free')) return; // Skip free plan
                
                const monthlyAmount = parseFloat(price.getAttribute('data-monthly'));
                const yearlyAmount = parseFloat(price.getAttribute('data-yearly'));
                if (monthlyAmount && yearlyAmount) {
                    const savings = ((monthlyAmount * 12) - yearlyAmount).toFixed(2);
                    price.setAttribute('data-savings', `Save $${savings}/year`);
                    // Update the display of savings
                    price.style.setProperty('--savings-amount', `'Save $${savings}/year'`);
                }
            });
        };

        // Initial update
        updatePricingSavings();
        
        // Update on toggle
        billingToggle.addEventListener('change', updatePricingSavings);
    }
});