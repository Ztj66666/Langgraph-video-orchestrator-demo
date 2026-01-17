import os
import requests
from moviepy import VideoFileClip, concatenate_videoclips


def download_video(url: str, save_path: str):
    """Download a video from a URL to the local file system"""
    print(f"[Utils] Downloading video: {url}")
    response = requests.get(url, stream=True)

    # 1. Get the directory path
    directory = os.path.dirname(save_path)

    # 2. Create the directory recursively if it doesn't exist (e.g., data/output)
    if directory and not os.path.exists(directory):
        print(f"Directory does not exist, creating: {directory}")
        os.makedirs(directory, exist_ok=True)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"[Utils] Download complete: {save_path}")
    else:
        raise Exception(f"Download failed, status code: {response.status_code}")


def merge_videos(video_paths: list, output_path: str):
    """Merge multiple local video clips into one"""
    if not video_paths:
        print("[Utils] No video clips found to merge")
        return

    print(f"[Utils] Merging {len(video_paths)} video clips...")

    clips = []
    try:
        # 1. Load all video clips
        for path in video_paths:
            if os.path.exists(path):
                clips.append(VideoFileClip(path))
            else:
                print(f"Warning: Clip not found at {path}")

        # 2. Concatenate videos
        final_video = concatenate_videoclips(clips, method="compose")

        # 3. Output the result (fps and codec can be adjusted here)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"[Utils] Final video generated: {output_path}")

    finally:
        # 4. Release resources (to prevent file locking)
        for clip in clips:
            clip.close()


if __name__ == "__main__":
    # --- Local Unit Test ---
    # Simulate two video segments (you can copy a previously downloaded video
    # twice into data/output and rename them for testing)
    test_output_dir = "../../data/output"
    os.makedirs(test_output_dir, exist_ok=True)

    # Please ensure there are actual local mp4 files here for testing
    test_clips = [
        os.path.join(test_output_dir, "clip_1.mp4"),
        os.path.join(test_output_dir, "clip_2.mp4")
    ]

    target_video = os.path.join(test_output_dir, "final_work.mp4")

    # If local test files exist, uncomment the line below to run the merge test
    # merge_videos(test_clips, target_video)