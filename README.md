# Multi-Agent Video Orchestration System

This project presents an AI-driven video generation pipeline that automates the transition from a sequence of static images into a cohesive cinematic short film. By utilizing the LangGraph framework, the system manages a sophisticated multi-agent workflow designed to address common challenges in generative video production, such as maintaining visual continuity and temporal consistency across different scenes.

---

## Technical Stack

* **Core Framework**: Python 3.10, LangGraph, LangChain
* **AI Models**: GPT-4o (Orchestration and Review), Alibaba Cloud Wanx 2.1 (Video Generation)
* **Multimedia Tools**: MoviePy, FFmpeg
* **Interfaces**: Gradio (Web), Command Line Interface (CLI), Model Context Protocol (MCP)

---

## System Architecture

The project uses a stateful multi-agent workflow where specialized agents collaborate to manage the generation process.

* **Orchestrator**: Analyzes the image sequence to create a storyboard with specific motion instructions to ensure the end of one segment matches the start of the next.
* **Workers**: Process tasks in parallel using the Wanx engine to transform images into 5-second video clips based on directed prompts.
* **Critic**: Inspects generated clips for visual consistency, quality, and adherence to safety guidelines.
* **Aggregator**: Reassembles the processed clips into a single file while maintaining the correct chronological order through an indexing system.
System Architecture
The system utilizes a stateful multi-agent workflow powered by LangGraph to orchestrate the video generation process.

Code snippet

graph TD
    A[Input Images & Topic] --> B[AI Orchestrator]
    B -->|Task Distribution| C1[Video Worker 1]
    B -->|Task Distribution| C2[Video Worker 2]
    B -->|Task Distribution| Cn[Video Worker n]
    
    C1 --> D[AI Critic]
    C2 --> D
    Cn --> D
    
    D -->|Approved| E[Sequential Aggregator]
    D -->|Feedback| B
    
    E --> F[Final Cinematic Video]
---

## Video Generation Model

The system currently utilizes the **wanx2.1-i2v-turbo** model via Alibaba Cloud DashScope. This is a cost-effective, entry-level model selected to balance performance with budget constraints. For users with sufficient account balance who require higher visual quality and improved motion consistency, the engine can be upgraded to more advanced models such as **wan2.6-i2v**.

To modify the generation engine, locate the model parameter in the `VideoSynthesis.async_call` function（src/utils/video_processor.py） within the tool implementation:

```python
rsp = VideoSynthesis.async_call(
    model='*wan2.6-i2v',  # Replace with 'wanx2.1-i2v-plus' for higher quality
    img_url=img_url,
    prompt=final_prompt
)

```

---

## Configuration

The system requires two primary API keys to be configured in a `.env` file located in the root directory:

* **OPENAI_API_KEY**: Used for the GPT-4o model which handles storyboard orchestration and automated segment review.
* **DASHSCOPE_API_KEY**: Connects to the Alibaba Cloud DashScope (百炼) platform to access the Wanx (万相) video synthesis engine.
* **MODE**: Set to `REAL` for live API calls or `MOCK` for testing the LangGraph workflow logic without incurring API costs.

---

## Usage and Setup

To run the system, first ensure all dependencies are installed by running `pip install -r requirements.txt`. Once the environment is ready, you can operate the system in three distinct modes:

1. **Web UI**: Execute `python src/web_ui.py` to launch an interactive Gradio dashboard for uploading images and monitoring the agent's real-time reasoning.
2. **CLI**: Run `python -m src.cli` to batch process image assets stored in the default `data/input` directory and output the final video.
3. **MCP Server**: Run `python src/mcp_server.py` to expose the orchestration logic as a tool for Model Context Protocol compatible clients, such as Claude Desktop.

---


---






