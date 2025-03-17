import subprocess
import os

# File paths
input_video = "final_video_output.mp4"
input_srt = "output_captions.srt"
output_video = "captioned_video.mp4"

# Check if files exist
if not os.path.exists(input_video):
    print(f"Error: {input_video} not found")
    exit(1)
if not os.path.exists(input_srt):
    print(f"Error: {input_srt} not found")
    exit(1)

def main():
    print("Burning captions...")

    # FFmpeg command to burn subtitles into the middle
    command = [
        "ffmpeg",
        "-i", input_video,                              # Input video
        "-vf", "subtitles=output_captions.srt:force_style='Alignment=10'",  # Subtitles centered
        "-c:v", "libx264",                             # Video codec
        "-c:a", "copy",                                # Copy audio without re-encoding
        output_video                                   # Output file
    ]

    # Run the command
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Subtitles burned successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running FFmpeg:")
        print(e.stderr)
    except FileNotFoundError:
        print("FFmpeg not found. Ensure it’s installed and added to your PATH.")

    # Verify output
    if os.path.exists(output_video):
        print(f"Output saved as {output_video}")
    else:
        print("Something went wrong. Output file not created.")

if __name__ == "__main__":
    main()