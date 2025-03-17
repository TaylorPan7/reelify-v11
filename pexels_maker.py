import requests
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy.video.fx.all import crop
from PIL import Image
import numpy as np
import os


# Your API keys
pexels_api_key = "XtuMUM4zwxKIPQc8UM4DcRbL2LMDgRPEF7E3b6Me9wmyXnA0oz3gcH2F"
gemini_api_key = "AIzaSyC6j1coXudHOiKjw0w4dNnp7k0Uxt9w2DM"


def get_gemini_response(prompt):
    """
    Fetches a script from the Gemini API based on the given topic.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    formatted_prompt = (
        f"write me a script for this topic, and return a paragraph form, "
        f"no longer than 80 seconds of continuous speech, without any sound effects, "
        f"narrator mentions, italics, bold formatting, or parentheses. {prompt}"
    )
    data = {
        "contents": [
            {
                "parts": [{"text": formatted_prompt}]
            }
        ]
    }


    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return content
    else:
        return f"Error: {response.status_code}, {response.text}"


async def text_to_speech(text, voice="en-US-AndrewMultilingualNeural", output_file="output.mp3"):
    """
    Converts text to speech using Edge TTS and saves the output as an MP3 file.
    """
    print(f"Using voice: {voice}")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"TTS audio saved as {output_file}")


def fetch_videos_from_pexels(query, num_videos=7):
    """
    Fetches exactly 7 video URLs from Pexels based on the query.
    """
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={num_videos}"
    headers = {"Authorization": pexels_api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        video_urls = [video["video_files"][0]["link"] for video in data["videos"]]
        return video_urls
    else:
        print(f"Error fetching videos: {response.status_code}, {response.text}")
        return []


def download_video(url, output_file):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            # Verify file was downloaded correctly
            if os.path.getsize(output_file) == 0:
                raise Exception("Downloaded file is empty")
            print(f"Downloaded video: {output_file}")
        else:
            raise Exception(f"Error downloading video: {response.status_code}")
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False
    return True


def resize_and_crop_to_9_16(video_clip):
    """
    Resizes and crops a video clip to a 9:16 aspect ratio (720x1280 pixels).
    """
    # Target resolution for 9:16 (portrait) videos
    target_width = 720
    target_height = 1280


    # Get the original dimensions of the video
    original_width, original_height = video_clip.size


    # Calculate the current aspect ratio
    current_aspect_ratio = original_width / original_height


    # Crop the video based on its aspect ratio
    if current_aspect_ratio < 9 / 16:
        # Video is too narrow (portrait), crop vertically
        new_height = round(original_width / (9 / 16))
        video_clip = crop(
            video_clip,
            width=original_width,
            height=new_height,
            x_center=original_width / 2,
            y_center=original_height / 2
        )
    else:
        # Video is too wide (landscape), crop horizontally
        new_width = round((9 / 16) * original_height)
        video_clip = crop(
            video_clip,
            width=new_width,
            height=original_height,
            x_center=original_width / 2,
            y_center=original_height / 2
        )


    # Custom resizing using Pillow to avoid ANTIALIAS error
    def resize_frame(frame):
        pil_image = Image.fromarray(frame)
        resized_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        return np.array(resized_image)


    # Apply the custom resizing function to each frame
    resized_clip = video_clip.fl_image(resize_frame)


    return resized_clip


def trim_clip_to_duration(video_clip, max_duration=10):
    """
    Trims a video clip to a maximum duration (e.g., 10 seconds).
    """
    if video_clip.duration > max_duration:
        video_clip = video_clip.subclip(0, max_duration)
    return video_clip


def create_video_with_audio(video_files, audio_file, output_file="final_video.mp4"):
    """
    Combines video clips and overlays audio to create a final video.
    """
    # Load each video clip, resize, crop, and trim it to 1-10 seconds
    video_clips = []
    for video in video_files:
        clip = VideoFileClip(video)
        clip = resize_and_crop_to_9_16(clip)  # Resize to 720x1280
        clip = clip.set_fps(30)               # Set frame rate to 30 FPS
        clip = trim_clip_to_duration(clip, max_duration=10)  # Trim to max 10 seconds
        video_clips.append(clip)


    # Concatenate all video clips
    final_video = concatenate_videoclips(video_clips, method="compose")


    # Load the audio file
    audio = AudioFileClip(audio_file)


    # Ensure the audio matches the video duration
    if audio.duration > final_video.duration:
        audio = audio.subclip(0, final_video.duration)  # Trim audio to match video length
    elif audio.duration < final_video.duration:
        final_video = final_video.subclip(0, audio.duration)  # Trim video to match audio length


    # Set the audio to the concatenated video
    final_video = final_video.set_audio(audio)


    # Write the final video to a file using 10 CPU cores
    final_video.write_videofile(
        output_file,
        codec="libx264",         # H.264 codec
        audio_codec="aac",       # AAC audio codec
        threads=10               # Use 10 out of 14 CPU cores
    )
    print(f"Final video saved as {output_file}")


if __name__ == "__main__":
    topic = input("Enter your topic: ")
    script_text = get_gemini_response(topic)
    if "Error" in script_text:
        print(f"Error generating script: {script_text}")
    else:
        print("Generated Script:\n", script_text)


        # Step 1: Generate MP3
        asyncio.run(text_to_speech(script_text))


        # Step 2: Fetch videos from Pexels
        keyword = topic.split()[0]  # Use only the first word of the topic as the keyword
        video_urls = fetch_videos_from_pexels(keyword, num_videos=7)


        # Step 3: Download videos
        valid_videos = []
        for i, url in enumerate(video_urls):
            video_file = f"video_{i + 1}.mp4"
            if download_video(url, video_file):
                valid_videos.append(video_file)
        
        if len(valid_videos) < 2:
            print("Error: Not enough valid videos downloaded")
            exit(1)


        # Step 4: Create the final video
        create_video_with_audio(valid_videos, "output.mp3")

