# Multi-Agent Video Orchestration System

This project implements an AI-driven video generation pipeline designed to convert static image sequences into cinematic short films with visual continuity. It utilizes a multi-agent framework to handle the complexities of temporal alignment and motion orchestration in generative media.

---

## Technical Stack

* **Core Framework**: Python 3.10, LangGraph, LangChain
* **AI Models**: GPT-4o (Orchestration and Planning), Alibaba Cloud Wanx (I2V Generation)
* **Multimedia Tools**: MoviePy, FFmpeg
* **Interfaces**: Gradio (Web), Command Line Interface (CLI), Model Context Protocol (MCP)

---

## System Architecture

The system is organized into a stateful workflow where multiple specialized agents collaborate to produce the final video.

* **Orchestrator**: Analyzes the input image sequence to create a detailed storyboard. It designs motion instructions to ensure the end of one segment matches the start of the next.
* **Workers**: Execute video generation in parallel. Each worker is responsible for a single segment, transforming the orchestrator's text instructions and the source image into a 5-second video clip.
* **Critic**: Performs an automated review of the generated clips to check for visual consistency and adherence to safety guidelines.
* **Aggregator**: Reassembles the processed clips. It uses an indexing system to maintain the correct chronological order during the final merge, regardless of the parallel processing speed.

---

## Installation and Setup

### Prerequisites

* Python 3.10 or higher
* FFmpeg installed on the system path
* API keys for OpenAI and Alibaba Cloud (DashScope)

### Setup

```bash
git clone https://github.com/Ztj66666/Langgraph-video-orchestrator-demo.git
cd Langgraph-video-orchestrator-demo
pip install -r requirements.txt

```

### Environment Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_key
DASHSCOPE_API_KEY=your_dashscope_key
MODE=REAL # Use MOCK for testing logic without API costs

```

---

## Usage

The system supports three operational modes:

1. **Web Interface**: Run `python src/web_ui.py` to use the Gradio dashboard for uploading images and monitoring the workflow.
2. **CLI Mode**: Run `python -m src.cli` to process images from `data/input` and output the results directly to `data/output`.
3. **MCP Server**: Run `python src/mcp_server.py` to connect the orchestrator as a tool for LLM clients like Claude Desktop.

---

## Future Development

Planned improvements include implementing autoregressive frame anchoring, where the last frame of a segment is used as the input for the next, and adding an automated background music (BGM) generation agent to match the video's mood.

Would you like me to help you format the project file structure section to reflect the actual folders in your repository?
