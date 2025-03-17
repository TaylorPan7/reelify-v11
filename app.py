from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import time
import random
import asyncio
import subprocess
from pathlib import Path
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store video generation progress
video_progress = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/socials')
def socials():
    return render_template('socials.html')

@app.route('/video-generator')
def video_generator():
    return render_template('video_generator.html')

@app.route('/image-generator')
def image_generator():
    return render_template('image_generator.html')

@app.route('/captioner')
def captioner():
    return render_template('captioner.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# Company pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/press')
def press():
    return render_template('press.html')

@app.route('/partners')
def partners():
    return render_template('partners.html')

# Resources pages
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

# Legal pages
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

@app.route('/gdpr')
def gdpr():
    return render_template('gdpr.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos/output', filename)

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory('static/output', filename)

async def run_video_generation(topic, video_id):
    try:
        # Initialize progress
        video_progress[video_id] = {
            'status': 'starting',
            'progress': 0,
            'current_step': 'Initializing...',
            'error': None
        }

        def update_progress(progress, step):
            print(f"Progress update: {progress}% - {step}")  # Debug logging
            video_progress[video_id] = {
                'status': 'in_progress',
                'progress': progress,
                'current_step': step,
                'error': None
            }

        # Create output directory
        output_dir = os.path.join('static', 'videos', 'output', video_id)
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Run pexels_maker.py (40%)
        update_progress(5, 'Generating script and downloading videos...')
        
        # Create a process to run pexels_maker.py and pipe the topic
        process = subprocess.Popen(
            ['python', 'pexels_maker.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the topic to the script
        stdout, stderr = process.communicate(input=f"{topic}\n")
        
        if process.returncode != 0:
            raise Exception(f"Failed to generate video: {stderr}")
        
        print("pexels_maker.py completed successfully")
        update_progress(40, 'Videos downloaded and combined')

        # Step 2: Run merge.py (60%)
        update_progress(45, 'Merging video and audio...')
        try:
            result = subprocess.run(['python', 'merge.py'], check=True, capture_output=True, text=True)
            print("merge.py output:", result.stdout)
            if result.stderr:
                print("merge.py stderr:", result.stderr)
            
            # Wait for the file to be created and check its existence
            time.sleep(2)  # Give some time for file operations to complete
            if not os.path.exists('final_video_output.mp4'):
                raise Exception("merge.py did not create final_video_output.mp4")
            
            update_progress(60, 'Video and audio merged')
        except subprocess.CalledProcessError as e:
            print(f"Error in merge.py: {e.stdout}\n{e.stderr}")
            raise Exception(f"Failed to merge video and audio: {e.stderr}")

        # Step 3: Run transcriber_script.py (80%)
        update_progress(65, 'Generating transcription...')
        try:
            # Check input file exists
            if not os.path.exists('final_video_output.mp4'):
                raise Exception("Input video file not found before transcription")
            
            result = subprocess.run(['python', 'transcriber_script.py'], check=True, capture_output=True, text=True)
            print("transcriber_script.py output:", result.stdout)
            if result.stderr:
                print("transcriber_script.py stderr:", result.stderr)
            
            # Wait for the file to be created and check its existence
            time.sleep(2)  # Give some time for file operations to complete
            if not os.path.exists('output_captions.srt'):
                raise Exception("transcriber_script.py did not create output_captions.srt")
            
            update_progress(80, 'Transcription generated')
        except subprocess.CalledProcessError as e:
            print(f"Error in transcriber_script.py: {e.stdout}\n{e.stderr}")
            raise Exception(f"Failed to generate transcription: {e.stderr}")

        # Step 4: Run captioned_video.py (100%)
        update_progress(85, 'Adding captions...')
        try:
            # Check input files exist
            if not os.path.exists('final_video_output.mp4'):
                raise Exception("Input video file not found before captioning")
            if not os.path.exists('output_captions.srt'):
                raise Exception("Input SRT file not found before captioning")
            
            result = subprocess.run(['python', 'captioned_video.py'], check=True, capture_output=True, text=True)
            print("captioned_video.py output:", result.stdout)
            if result.stderr:
                print("captioned_video.py stderr:", result.stderr)
            
            # Wait for the file to be created and check its existence
            time.sleep(2)  # Give some time for file operations to complete
            if not os.path.exists('captioned_video.mp4'):
                raise Exception("captioned_video.py did not create captioned_video.mp4")
            
        except subprocess.CalledProcessError as e:
            print(f"Error in captioned_video.py: {e.stdout}\n{e.stderr}")
            raise Exception(f"Failed to add captions: {e.stderr}")

        # Check if files exist before moving
        final_video = 'captioned_video.mp4'
        output_video = os.path.join(output_dir, 'final_video.mp4')
        srt_file = 'output_captions.srt'
        output_srt = os.path.join(output_dir, 'captions.srt')

        if not os.path.exists(final_video):
            raise Exception(f"Final video file not found: {final_video}")
        if not os.path.exists(srt_file):
            raise Exception(f"SRT file not found: {srt_file}")

        # Move the files
        os.rename(final_video, output_video)
        os.rename(srt_file, output_srt)

        # Update final status
        video_progress[video_id] = {
            'status': 'completed',
            'progress': 100,
            'current_step': 'Video generation completed!',
            'error': None,
            'video_url': f'/videos/{video_id}/final_video.mp4',
            'srt_url': f'/videos/{video_id}/captions.srt'
        }
        print("Video generation completed successfully")

    except Exception as e:
        error_message = str(e)
        print(f"Error generating video: {error_message}")
        video_progress[video_id] = {
            'status': 'error',
            'progress': 0,
            'current_step': 'Error occurred',
            'error': error_message
        }

@app.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate a unique ID for this video
        video_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        try:
            # Start the async video generation
            asyncio.run(run_video_generation(topic, video_id))
            
            return jsonify({
                'success': True,
                'video_id': video_id,
                'message': 'Video generation started'
            })
        except Exception as e:
            # Log the error for debugging
            print(f"Error in video generation process: {str(e)}")
            return jsonify({
                'error': f'Failed to start video generation: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Invalid request format'}), 400

@app.route('/check-video-status/<video_id>')
def check_video_status(video_id):
    try:
        if video_id not in video_progress:
            return jsonify({
                'status': 'not_found',
                'error': 'Video generation not found'
            }), 404

        progress = video_progress[video_id]
        
        # If the video is completed, clean up the progress data
        if progress['status'] == 'completed':
            response_data = progress.copy()
            del video_progress[video_id]  # Clean up progress data
            return jsonify(response_data)
            
        return jsonify(progress)
        
    except Exception as e:
        print(f"Error checking video status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'Failed to check video status: {str(e)}'
        }), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    # Placeholder for image generation
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # In a real implementation, this would call an image generation API
        # For now, we'll simulate this step
        
        # Return a placeholder image URL
        return jsonify({
            'success': True,
            'image_url': '/static/sample-image.jpg',
            'message': 'Image generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-captions', methods=['POST'])
def generate_captions():
    # Placeholder for caption generation
    try:
        # In a real implementation, this would process the uploaded video
        # and generate captions
        
        # Return placeholder data
        return jsonify({
            'success': True,
            'captions': [
                {'start': '00:00:02', 'end': '00:00:05', 'text': 'This is a sample caption.'},
                {'start': '00:00:06', 'end': '00:00:09', 'text': 'Generated automatically by our system.'},
                {'start': '00:00:10', 'end': '00:00:14', 'text': 'You can download the captioned video below.'}
            ],
            'video_url': '/static/sample-captioned-video.mp4',
            'srt_url': '/static/sample-captions.srt',
            'message': 'Captions generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
