
# Multi-Agent Video Orchestration System

This project presents an AI-driven video generation pipeline that automates the transition from a sequence of static images into a cohesive cinematic short film. By utilizing the LangGraph framework, the system manages a sophisticated multi-agent workflow designed to address common challenges in generative video production, such as maintaining visual continuity, temporal consistency, and logical movement across different scenes.

---

## System Architecture

The core of the system is built around a decentralized Orchestrator-Worker-Critic model. The AI Orchestrator serves as the lead director, analyzing the visual features of the input images to design a storyboard that emphasizes motion momentum and spatial alignment between consecutive frames. These tasks are then distributed to Parallel Video Workers, which execute the image-to-video (I2V) generation concurrently using high-performance generative models. To ensure the final output meets quality and safety standards, an AI Critic reviews the segments, while a Sequential Aggregator utilizes an indexed state management system to reassemble the clips in the correct chronological order, ensuring that the final merge remains accurate despite the asynchronous nature of the generation process.

---

## Key Features

The system implements advanced prompting strategies to achieve cinematic Match Cut transitions, ensuring that the ending of one segment naturally flows into the beginning of the next. By leveraging the stateful nature of LangGraph, the pipeline is highly robust, supporting error recovery and the potential for human-in-the-loop intervention at critical decision points. For performance optimization, the system utilizes asynchronous task distribution to reduce total processing time. It supports multiple interfaces, including a Gradio web dashboard for interactive use, a Command Line Interface (CLI) for batch processing, and a Model Context Protocol (MCP) server for integration with LLM clients like Claude Desktop.

---

## Technical Stack

The backend is developed in Python 3.10 and powered by the LangGraph and LangChain libraries for workflow management. The generative capabilities are provided by GPT-4o for orchestration and the Alibaba Cloud Wanx engine for video synthesis. Multimedia operations, including clip merging and frame adjustments, are handled via MoviePy and FFmpeg. The user interface is built with Gradio, providing a real-time visualization of the system topology and generation logs.

---

## Installation and Setup

### Prerequisites
Ensure that Python 3.10+ is installed along with FFmpeg. You will also require active API credentials for OpenAI and Alibaba Cloud (DashScope).

### Installation
Clone the repository and install the required dependencies:
```bash
git clone [https://github.com/Ztj66666/Langgraph-video-orchestrator-demo.git](https://github.com/Ztj66666/Langgraph-video-orchestrator-demo.git)
cd Langgraph-video-orchestrator-demo
pip install -r requirements.txt

```

### Configuration

Create a .env file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_key
DASHSCOPE_API_KEY=your_dashscope_key
MODE=REAL # Set to MOCK for logic testing without API calls

```

---

## Usage Instructions

The system can be operated in three distinct modes depending on the user's requirements:

1. Web Interface: Run python src/web_ui.py to launch the interactive dashboard for uploading images and monitoring the agent's reasoning in real-time.
2. Command Line: Run python -m src.cli to automatically process images stored in the data/input directory and generate a final video.
3. MCP Server: Run python src/mcp_server.py to expose the orchestration logic as a tool for compatible LLM environments.

---

## Project Context

Developed as a project in Applied Artificial Intelligence, this system explores the intersection of multi-agent collaboration and multimodal generative workflows. It addresses the technical difficulties of pixel-level continuity and temporal alignment in AI-generated media. Future development will focus on integrating autoregressive frame anchoring and automated cinematic scoring.

```

```


