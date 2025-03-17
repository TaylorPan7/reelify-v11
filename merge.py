from moviepy.editor import VideoFileClip, AudioFileClip
import os

def main():
    try:
        print("Combining videos...")
        if not os.path.exists("final_video.mp4") or not os.path.exists("output.mp3"):
            print("Error: Required input files not found")
            return

        # Load the video and audio clips
        videoclip = VideoFileClip("final_video.mp4")
        audioclip = AudioFileClip("output.mp3")

        # Set the audio of the video clip
        videoclip_with_audio = videoclip.set_audio(audioclip)

        # Write the final video to a file with the specified codec
        videoclip_with_audio.write_videofile("final_video_output.mp4", codec='libx264')

        # Close the clips to release the resources
        videoclip.close()
        audioclip.close()

        # List of files to delete
        files_to_delete = [
            "final_video.mp4",
            "output.mp3",
            "video_1.mp4",
            "video_2.mp4",
            "video_3.mp4",
            "video_4.mp4",
            "video_5.mp4",
            "video_6.mp4",
            "video_7.mp4"
        ]

        # Delete the specified files
        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)
                print(f"Deleted {file}")
            else:
                print(f"{file} not found")

    except Exception as e:
        print(f"Error during video merging: {str(e)}")
    finally:
        try:
            files_to_delete = ["final_video.mp4", "output.mp3"]
            for file in files_to_delete:
                if os.path.exists(file):
                    os.remove(file)
        except:
            pass

if __name__ == "__main__":
    main()
