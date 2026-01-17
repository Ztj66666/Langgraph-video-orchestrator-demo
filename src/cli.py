import os
import glob
from src.agents.workflow import app


def run_cli():
    print("🚀 AI Video Orchestration System - CLI Mode")

    # 1. Automatically scan for images
    input_pattern = os.path.join("data/input", "*.[jp][pn]g")  # Matches jpg, png
    image_paths = sorted(glob.glob(input_pattern))

    if not image_paths:
        print("❌ Error: No image assets found in the data/input directory")
        return

    topic = input("Please enter video topic (default: General Theme): ") or "General Theme"

    print(f"--- Found {len(image_paths)} images, starting generation ---")

    # 2. Run the workflow
    inputs = {
        "image_paths": [os.path.abspath(p) for p in image_paths],
        "video_topic": topic,
        "video_clips": []
    }

    config = {"configurable": {"thread_id": "cli_run"}}

    for output in app.stream(inputs, config=config):
        for node, state in output.items():
            print(f"[{node}]: Completed")

            # Print prompt only if the node is video_worker
            if node == "video_worker" and isinstance(state, dict):
                prompt = state.get('current_prompt')
                task_id = state.get('current_task_id', 'Unknown Task')

                # Defensive logic: if prompt is None, convert to empty string or warning
                if prompt is not None:
                    display_prompt = prompt[:50]
                else:
                    display_prompt = "⚠️ Warning: Node did not return a valid prompt"

                print(f"   🎬 Task ID: {task_id}")
                print(f"   🎬 Prompt: {display_prompt}...")

            if node == "aggregate_videos":
                final_path = state.get('final_video_path', 'Failed to retrieve path')
                print(f"✅ Final video generated: {final_path}")


if __name__ == "__main__":
    run_cli()