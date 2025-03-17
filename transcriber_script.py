import assemblyai as aai
import subprocess
import os

aai.settings.api_key = "07d0b3d1ff004575932b2a7f0f37fe10"

def extract_audio(video_path, audio_path):
    """Extracts audio from an MP4 file using FFmpeg."""
    print(f"Extracting audio from {video_path} to {audio_path}")
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"],
            check=True, capture_output=True, text=True
        )
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Failed to extract audio. {audio_path} not found.")
        print("Audio extraction complete")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        raise
    except FileNotFoundError as e:
        print(f"Error: FFmpeg not found. Ensure it's installed and in your PATH.")
        raise

def transcribe_audio(audio_path):
    """Uploads audio to AssemblyAI and returns the transcript with word-level timing."""
    print(f"Transcribing {audio_path} with AssemblyAI")
    config = aai.TranscriptionConfig(auto_highlights=False)  # Basic config, adjust as needed
    transcriber = aai.Transcriber()
    
    # Create a file object and get the file path
    transcript = transcriber.transcribe(audio_path, config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription error: {transcript.error}")
    print("Transcription complete")
    return transcript

def generate_word_level_srt(transcript, output_srt_path):
    """Generates an SRT file with individual word timestamps."""
    print(f"Generating word-level SRT to {output_srt_path}")
    srt_content = []
    for i, word_info in enumerate(transcript.words, 1):  # Start index at 1
        start_ms = word_info.start
        end_ms = word_info.end
        # Convert milliseconds to SRT timestamp format (HH:MM:SS,MMM)
        start_time = f"{start_ms // 3600000:02d}:{(start_ms // 60000) % 60:02d}:{(start_ms // 1000) % 60:02d},{start_ms % 1000:03d}"
        end_time = f"{end_ms // 3600000:02d}:{(end_ms // 60000) % 60:02d}:{(end_ms // 1000) % 60:02d},{end_ms % 1000:03d}"
        srt_entry = f"{i}\n{start_time} --> {end_time}\n{word_info.text}\n"
        srt_content.append(srt_entry)
    
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write("\n".join(srt_content))
    print("Word-level SRT saved")

def main():
    print("Starting transcription process...")
    video_path = "final_video_output.mp4"
    audio_path = "temp_audio.wav"
    output_srt_path = "output_captions.srt"
    
    # List all files in current directory
    print("Files in current directory:")
    for file in os.listdir('.'):
        print(f"- {file}")
    
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found")
        print(f"Current working directory: {os.getcwd()}")
        return
    
    try:
        print(f"Found video file: {video_path}")
        print(f"Video file size: {os.path.getsize(video_path)} bytes")
        extract_audio(video_path, audio_path)
        transcript = transcribe_audio(audio_path)
        generate_word_level_srt(transcript, output_srt_path)
        os.remove(audio_path)
        print(f"Word-level SRT file saved as {output_srt_path}")
    except Exception as e:
        print(f"Process failed: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)  # Cleanup even on failure

if __name__ == "__main__":
    main()