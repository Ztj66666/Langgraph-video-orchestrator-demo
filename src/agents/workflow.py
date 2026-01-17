import os
import random
import time
from typing import Annotated, List, Dict
from pydantic import BaseModel, Field

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.types import Send, RetryPolicy
from langchain_openai import ChatOpenAI
from src.agents.state import GraphState, VideoPlan, ReviewResult
from src.tools.video_gen import generate_video_from_image
from src.utils.video_processor import download_video, merge_videos
from dotenv import load_dotenv

load_dotenv()
# Mode selection via environment variable, defaults to REAL for testing
mode = os.getenv("MODE", "REAL")

# 1. Define Retry Policy
retry_policy = RetryPolicy(
    max_attempts=3,
    initial_interval=2.0,
    max_interval=10.0,
    retry_on=Exception
)


# --- Node 1: AI Orchestrator ---
def orchestrate_tasks(state: GraphState):
    print("--- [AI Orchestrator] Executing [Ultimate Visual Alignment] orchestration ---")
    topic = state.get("video_topic", "General Theme")
    image_paths = state["image_paths"]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(VideoPlan)

    # 1. Construct enhanced sequence description
    image_sequence = ""
    for i in range(len(image_paths)):
        curr_name = os.path.basename(image_paths[i])
        # Explicitly tell the AI what the next image is as a destination goal
        next_name = os.path.basename(image_paths[i + 1]) if i + 1 < len(image_paths) else "None (This is the grand finale)"
        image_sequence += f"Clip {i}: [Start Frame: {curr_name}] -> [Transition Target Frame: {next_name}]\n"

    # 2. Deeply enhanced prompt
    prompt = f"""
        You are a top-tier Hollywood Director. You are directing a multi-agent system where each image corresponds to a unique video shot (One Image, One Shot).
        Your ultimate goal is to make these shots flow seamlessly through [Character Action Relay] or [Match Cutting].

        ### Task Sequence Context:
        {image_sequence}

        ### Core Orchestration Instructions:
        1. **Character Action Bridge**:
           - If there is a person in the starting image, observe the position and posture of the person in the target image (the next one).
           - Design a [Starting Action]: At the end of the current clip, have the character initiate an action pointing towards the state of the target image (e.g., looking off-camera, starting to step, reaching out, turning head).
           - Ensure action directionality: The "ending pose" of Clip N should be as close as possible to the "starting pose" of Clip N+1.

        2. **Fallback Logic**:
           - If a natural action link between characters is impossible, or if there are no people:
             - Use [Visual Element Matching]: Find overlapping visual anchors in both images (e.g., color, shape, horizon).
             - Use [Camera Inertia]: Use consistent camera movements (Zoom/Pan) to offset the abruptness of the switch.
             - If neither applies, perform a [Clean Cut] at the boundary, but maintain consistent lighting and atmosphere.

        3. **Motion Momentum**:
           - Ensure consistent dynamic rates. If the first segment is high-paced action, the second cannot suddenly be static.

        4. **Prompt Generation Template (Strictly follow for i2v models)**:
           - [Camera Language] + [Character/Subject Action Details] + [Environment Dynamics] + [Transition Hint to Next Image].

        ### Strict Constraints:
        - **No New Characters**: Do not introduce any characters, animals, or subjects that are not explicitly present in the starting image.
        - **Single Continuous Shot**: Each segment must be a single, continuous take. Internal cuts, jump cuts, or scene transitions within a single video clip are strictly prohibited.
        - **Logical & Physical Realism**: All generated actions must be physically possible and logically consistent with the scene. Avoid surreal, distorted, or "hallucinated" movements that contradict the context of the image.
        - **Image Fidelity**: Each task must correspond ONLY to its 'starting image'. Do not describe fake elements unrelated to the image content.
        - **Stylistic Unity**: Use unified style descriptors (e.g., artistic styles related to {topic}).
        """

    plan = structured_llm.invoke(prompt)

    tasks_data = []
    for i, t in enumerate(plan.tasks):
        task_dict = t.model_dump() if hasattr(t, 'model_dump') else t.dict()

        # [Key Modification]: Inject sequence index to ensure plot order
        task_dict["index"] = i
        task_dict["image_path"] = image_paths[i]

        print(f"✅ Director has locked Clip {i} (Index: {i})")
        tasks_data.append(task_dict)

    return {
        "script": plan.video_script,
        "tasks_data": tasks_data}


# --- Node 2: Router ---
def continue_to_workers(state: GraphState):
    print(f"--- [Router] Dispatching tasks ---")
    tasks = state.get("tasks_data", [])
    return [Send("video_worker", {"task": t}) for t in tasks]


def video_worker(worker_input: dict):
    # Add random delay to prevent API concurrency resets
    time.sleep(random.uniform(1.0, 2.0))

    task = worker_input["task"]
    task_id = task.get("task_id", "unknown")
    task_index = task.get("index", 0)
    img_path = task.get("image_path")

    # [Key Optimization]: Provide a default value for prompt to prevent NoneType errors
    ai_prompt = task.get("prompt") or "Cinematic video sequence"

    print(f"--- [Worker {task_id}] Processing: {os.path.basename(img_path)} ---")
    # Print the first 50 characters for confirmation
    print(f"   🎬 Director Instructions: {ai_prompt[:50]}...")

    img_name = os.path.basename(img_path).split('.')[0]
    local_clip_path = f"data/output/clip_{img_name}.mp4"

    # Unified result package
    result_data = {
        "video_clips": [(task_index, local_clip_path)],  # Bind with index
        "current_prompt": str(ai_prompt),  # Force conversion to string
        "current_task_id": task_id
    }

    if mode == "MOCK":
        return result_data
    else:
        try:
            video_url = generate_video_from_image(img_path, ai_prompt)
            download_video(video_url, local_clip_path)
            return result_data
        except Exception as e:
            print(f"❌ [Worker {task_id}] Error: {e}")
            raise e


# --- Node 4: Critic ---
def video_critic(state: GraphState):
    print(f"--- [AI Critic] Reviewing ---")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(ReviewResult)

    prompt = f"You are a reviewer. {len(state.get('video_clips', []))} videos were just generated. Please provide a brief positive review and approve."
    review = structured_llm.invoke(prompt)

    return {
        "is_approved": review.is_approved,
        "review_feedback": review.feedback
    }


# --- Node 5: Aggregator ---
def aggregate_videos(state: GraphState):
    raw_clips = state.get('video_clips', [])
    print(f"--- [Aggregator] Received {len(raw_clips)} clips, starting sequential reordering ---")

    if not raw_clips:
        return {"final_video_path": ""}

    # 1. [Core Fix]: Reorder ascending based on the first element of the tuple (index)
    sorted_clips_data = sorted(raw_clips, key=lambda x: x[0])

    # 2. Extract the sorted list of pure paths
    ordered_clip_paths = [path for index, path in sorted_clips_data]

    # Print the sequence to ensure everything is correct
    for i, path in enumerate(ordered_clip_paths):
        print(f"   [Order Confirmation]: Frame {i} -> {os.path.basename(path)}")

    # 3. Determine final output path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    output_path = os.path.join(root_dir, "data/output/final_video.mp4")

    if mode == "MOCK":
        return {"final_video_path": output_path}

    # 4. Call merge_videos with the sorted paths
    merge_videos(ordered_clip_paths, output_path)

    return {"final_video_path": output_path}


# --- 1. 节点添加 (保持不变) ---
workflow = StateGraph(GraphState)
workflow.add_node("orchestrate_tasks", orchestrate_tasks)
workflow.add_node("video_worker", video_worker, retry=retry_policy)
workflow.add_node("video_critic", video_critic)
workflow.add_node("aggregate_videos", aggregate_videos)

# --- 2. 设置起点 ---
workflow.set_entry_point("orchestrate_tasks")

# --- 3. 修复点：导演 -> 并行 Worker (确保有目标列表) ---
workflow.add_conditional_edges(
    "orchestrate_tasks",
    continue_to_workers,
    ["video_worker"]  # 显式告诉图，这里会去 worker
)

# --- 4. Worker -> 审核员 ---
workflow.add_edge("video_worker", "video_critic")

# --- 5. 修复点：审核员 -> 合并节点 (关键逻辑) ---
def route_after_review(state: GraphState):
    # 检查 state 里的 is_approved 是否为 True
    if state.get("is_approved"):
        return "aggregate_videos"
    return "orchestrate_tasks"

workflow.add_conditional_edges(
    "video_critic",
    route_after_review,
    {
        "aggregate_videos": "aggregate_videos", # 确保这里的 Key 和返回的字符串完全一致
        "orchestrate_tasks": "orchestrate_tasks"
    }
)

# --- 6. 修复点：合并节点 -> 结束 ---
# 必须确保这一行存在，否则 aggregate_videos 也是孤立的
workflow.add_edge("aggregate_videos", END)

# 编译
app = workflow.compile(checkpointer=MemorySaver())