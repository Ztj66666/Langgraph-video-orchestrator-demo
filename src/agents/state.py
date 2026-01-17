import operator
from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field


# 定义一个简单的还原逻辑：总是取最新的值
def take_latest(left: str, right: str) -> str:
    return right


class GraphState(TypedDict):
    image_paths: List[str]
    video_topic: str
    video_clips: Annotated[list, operator.add]  # 这里的 operator.add 是 List 的还原器
    tasks_data: List[dict]
    script: str
    is_approved: bool
    review_feedback: str

    # 【核心修复】：为并行冲突的键添加 Annotated 和还原函数
    current_prompt: Annotated[str, take_latest]
    current_task_id: Annotated[str, take_latest]

class VideoTask(BaseModel):
    task_id: str = Field(description="Unique identifier for the task, e.g., clip_0, clip_1")
    image_path: str = Field(description="The original image path corresponding to this clip")
    prompt: str = Field(description="Dynamic video description generated for the image, e.g., 'The camera slowly zooms in, firelight flickering in the background'")

class VideoPlan(BaseModel):
    video_script: str = Field(description="Overall script summary for the entire video")
    tasks: List[VideoTask] = Field(description="List of specific video generation tasks after decomposition")

class ReviewResult(BaseModel):
    is_approved: bool = Field(description="Whether the review is approved. For the current stage, please ensure this returns True")
    feedback: str = Field(description="Specific evaluation or improvement suggestions for the video clip")