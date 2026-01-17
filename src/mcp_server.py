from mcp.server.fastmcp import FastMCP
from src.agents.workflow import app
import os

# Create MCP instance
mcp = FastMCP("VideoOrchestrator")


@mcp.tool()
def generate_ai_video(image_folder: str, topic: str) -> str:
    """
    Automatically orchestrates and generates a video with visual continuity
    based on the images and topic in a specified folder.
    :param image_folder: The local absolute path where the images are located.
    :param topic: The thematic description of the video.
    """
    # 1. Retrieve images
    files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg'))])
    image_paths = [os.path.join(image_folder, f) for f in files]

    if not image_paths:
        return "Error: No images found in the specified folder."

    # 2. Invoke LangGraph
    inputs = {"image_paths": image_paths, "video_topic": topic, "video_clips": []}
    result = app.invoke(inputs, config={"configurable": {"thread_id": "mcp_run"}})

    return f"Video generation successful! Storage path: {result.get('final_video_path')}"


if __name__ == "__main__":
    mcp.run()