import os
import time
import dashscope
from dashscope import VideoSynthesis
from dotenv import load_dotenv
from http import HTTPStatus

# Load environment variables
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def generate_video_from_image(image_path: str, prompt: str = None) -> str:
    # 1. Path processing: Convert relative path to absolute path
    abs_image_path = os.path.abspath(image_path)
    if not os.path.exists(abs_image_path):
        raise FileNotFoundError(f"Image not found: {abs_image_path}")

    # Alibaba Cloud SDK requires local file path format
    img_url = f"file://{abs_image_path}"

    print(f"[API] Submitting task, image path: {abs_image_path}")

    final_prompt = prompt if prompt else "A cinematic video with smooth camera movement, high quality"

    print(f"[API] Submitting task, Prompt: {final_prompt[:30]}...")

    rsp = VideoSynthesis.async_call(
        model='wanx2.1-i2v-turbo',  # Note: i2v (Image-to-Video) models are recommended for image-based generation
        img_url=img_url,
        prompt=final_prompt  # Use the dynamically passed description
    )

    # 3. Check submission status
    if rsp.status_code != HTTPStatus.OK:
        raise Exception(f"Submission failed! Error code: {rsp.code}, Message: {rsp.message}")

    task_id = rsp.output.task_id
    print(f"[API] Task submitted successfully, Task ID: {task_id}")

    # 4. Polling for task results
    while True:
        # Core fix: Parameter name must be 'task', not 'task_id'
        # Or pass task_id directly (without parameter name)
        status_rsp = VideoSynthesis.fetch(task=task_id)

        if status_rsp.status_code != HTTPStatus.OK:
            raise Exception(f"Polling error: {status_rsp.message}")

        # Get task status
        # Note: Ensure output exists and contains task_status
        task_status = status_rsp.output.task_status

        if task_status == 'SUCCEEDED':
            video_url = status_rsp.output.video_url
            print(f"[API] Video generated successfully! URL: {video_url}")
            return video_url
        elif task_status == 'FAILED':
            # Attempt to capture error cause on failure
            msg = getattr(status_rsp.output, 'message', 'Unknown error')
            raise Exception(f"Failed to generate video: {msg}")
        else:
            # Status is PENDING or RUNNING
            print(f"--- Current task status: {task_status}, please wait... ---")
            time.sleep(5)

if __name__ == "__main__":
    # Use absolute path to locate data/input/test1.jpg in the root directory
    current_dir = os.path.dirname(__file__)  # src/tools
    root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    test_img = os.path.join(root_dir, "data", "input", "test1.jpg")

    try:
        url = generate_video_from_image(test_img)
        print(f"\nFinal result: {url}")
    except Exception as e:
        print(f"\nTest error: {e}")