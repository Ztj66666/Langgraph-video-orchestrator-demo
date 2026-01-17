import asyncio
import sys
import gradio as gr
import os
import uuid
import shutil
import base64
import time
from src.agents.workflow import app

# Optimization for asyncio errors on Windows environment
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_graph_html(workflow_app):
    """
    Renders the system architecture diagram using Mermaid.ink
    """
    try:
        mermaid_code = workflow_app.get_graph().draw_mermaid()
        encoded_string = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        url = f"https://mermaid.ink/img/{encoded_string}"
        return f'''
        <div style="background-color: white; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd;">
            <img src="{url}" style="max-width: 100%; height: auto;" />
        </div>
        '''
    except Exception as e:
        return f"<p style='color:red;'>[System Error] Unable to generate flowchart: {e}</p>"


def process_video_flow(input_images, video_topic):
    # 1. Prepare Workspace
    thread_id = str(uuid.uuid4())[:8]
    input_dir = f"data/input/{thread_id}"
    os.makedirs(input_dir, exist_ok=True)

    image_paths = []
    if input_images:
        for i, img_obj in enumerate(input_images):
            # Normalizing paths for Windows compatibility
            target_path = os.path.abspath(os.path.join(input_dir, f"{i}.png")).replace('\\', '/')
            shutil.copy(img_obj.name, target_path)
            image_paths.append(target_path)

    # 2. Construct Graph Input
    inputs = {
        "image_paths": image_paths,
        "video_topic": video_topic,
        "video_clips": []
    }
    config = {"configurable": {"thread_id": thread_id}}

    status_log = "🚀 [System] Starting multi-agent video orchestration workflow...\n"
    yield status_log, None

    # 3. Execute Workflow and Stream Updates
    final_video_path = None
    try:
        for output in app.stream(inputs, config=config):
            for node_name, state_update in output.items():
                if state_update is None or not isinstance(state_update, dict):
                    continue

                if node_name == "orchestrate_tasks":
                    status_log += f"\n[AI Director]: Storyboard planning completed. Initiating parallel generation..."

                elif node_name == "video_worker":
                    task_id = state_update.get("current_task_id", "N/A")
                    prompt = state_update.get("current_prompt", "No description")
                    status_log += f"\n----------------------------------------"
                    status_log += f"\n[Worker]: Segment {task_id} generated successfully."
                    status_log += f"\n🎬 Prompt: {prompt[:100]}...\n"

                elif node_name == "video_critic":
                    feedback = state_update.get("review_feedback", "Approved")
                    status_log += f"\n[AI Critic]: {feedback}"

                elif node_name == "aggregate_videos":
                    raw_path = state_update.get("final_video_path")
                    if raw_path:
                        # Fix: Ensure path uses forward slashes for Gradio/Windows compatibility
                        final_video_path = os.path.abspath(raw_path).replace('\\', '/')
                        status_log += f"\n========================================"
                        status_log += f"\n✅ SUCCESS: All segments merged into final work."
                        status_log += f"\n📍 Location: {final_video_path}"

                # Continuous update to UI
                yield status_log, final_video_path

        # 4. Final safety yield to ensure the video component updates
        time.sleep(0.5)  # Buffer for MoviePy file closing
        yield status_log, final_video_path

    except Exception as e:
        status_log += f"\n\n❌ [Runtime Error]: {str(e)}"
        if "inappropriate" in str(e).lower():
            status_log += f"\n💡 Hint: Content safety filter triggered. Please try different images."
        yield status_log, None


# --- Build Gradio Interface ---
with gr.Blocks(title="AI Video Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 AI Video Multi-Agent Orchestration System")
    gr.Markdown(
        "An autonomous pipeline using **LangGraph** (Orchestrator-Worker-Critic) for seamless cinematic video creation.")

    with gr.Tabs():
        with gr.TabItem("Creation Studio"):
            with gr.Row():
                with gr.Column(scale=1):
                    input_files = gr.File(label="Step 1: Upload Assets", file_count="multiple", file_types=["image"])
                    topic_input = gr.Textbox(label="Step 2: Video Theme",
                                             placeholder="e.g., Cyberpunk neon city at night")
                    run_btn = gr.Button("🚀 Run Workflow", variant="primary")

                with gr.Column(scale=2):
                    status_window = gr.Textbox(label="Live Execution Logs & Storyboard", lines=15, interactive=False)
                    output_video = gr.Video(label="Final Cinematic Result")

        with gr.TabItem("System Topology"):
            gr.Markdown("### Real-time Agentic Workflow Architecture")
            # Refreshing graph HTML
            chart_html = get_graph_html(app)
            gr.HTML(value=chart_html)

    run_btn.click(
        fn=process_video_flow,
        inputs=[input_files, topic_input],
        outputs=[status_window, output_video]
    )

if __name__ == "__main__":
    # Ensure project paths are normalized
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(base_dir, "../data/output")).replace('\\', '/')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"--- Server Initialized ---")
    print(f"Standardized Output Directory: {output_dir}")

    demo.launch(
        share=True,
        allowed_paths=[output_dir]
    )