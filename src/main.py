import os
import argparse
import uuid
from src.agents.workflow import app


def get_images_from_dir(directory):
    """Scan the folder for valid image files"""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    images = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.lower().endswith(valid_extensions)
    ]
    return sorted(images)  # Sort to ensure controllable video sequence


def main():
    # 1. Define command-line arguments
    parser = argparse.ArgumentParser(description="LangGraph Video Orchestrator")
    parser.add_argument("--input", type=str, default="../data/input", help="Input folder path for images")
    parser.add_argument("--output", type=str, default="../data/output/final_video.mp4", help="Output video path")
    parser.add_argument("--thread_id", type=str, default=str(uuid.uuid4())[:8], help="Unique task identifier")

    args = parser.parse_args()

    # 2. Dynamically fetch images
    image_paths = get_images_from_dir(args.input)

    if not image_paths:
        print(f"Error: No valid image files (jpg/png/webp) found in {args.input}")
        return

    print(f"--- Starting Workflow ---")
    print(f"Number of images detected: {len(image_paths)}")
    print(f"Task ID: {args.thread_id}")

    # 3. Construct initial state
    # Note: We can pass the output path via config or extend it in inputs
    inputs = {
        "image_paths": image_paths,
        "video_clips": []
    }

    config = {"configurable": {"thread_id": args.thread_id}}

    # 4. Run
    for output in app.stream(inputs, config=config):
        # Add some visual feedback
        for node_name, state_update in output.items():
            print(f"\n[Node Completed]: {node_name}")

            # --- Core Fix: Add check for state_update is not None ---
            if state_update and 'video_clips' in state_update:
                clips = state_update['video_clips']
                # Compatibility handling: some nodes return a single path string, others a list
                count = len(clips) if isinstance(clips, list) else 1
                print(f"Clips generated so far: {count}")

    print(f"\nCongratulations! Task completed. Final video saved to: {args.output}")


if __name__ == "__main__":
    main()