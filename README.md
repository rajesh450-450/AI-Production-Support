# AI Production Support Platform

An enterprise-oriented AI application designed to assist production support teams with incident analysis, knowledge retrieval, troubleshooting, and evidence-based resolution recommendations.

The platform combines **LLM-powered agents, Retrieval-Augmented Generation (RAG), and workflow orchestration** to make production support investigation more structured and efficient.

## Key Features

- **Agent-based workflow:** Planner, Executor, Reviewer, and Answer agents orchestrated using LangGraph.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant knowledge using FAISS-based semantic search.
- **Knowledge management:** Uses SQLite for knowledge storage and authoritative retrieval of indexed content.
- **Incident lookup:** Supports exact-match lookup of locally stored Jira-style incident records.
- **Context assembly:** Combines and ranks relevant evidence to provide context for downstream reasoning.
- **LLM integration:** Uses Google Gemini for LLM-powered processing.
- **Local indexing:** Provides a pipeline for preparing knowledge sources for retrieval.
- **Modular architecture:** Separates workflow orchestration, retrieval, context building, and agent responsibilities.

## Architecture Overview

The application follows a structured workflow:

```text
User Question
     |
     v
   Planner
     |
     v
Retrieval Service
     |
     v
Knowledge Retriever
(FAISS + SQLite)
     |
     v
  Context Builder
     |
     v
   Executor
     |
     v
   Reviewer
     |
     v
  Final Answer
```

The workflow is designed to support review and controlled retries when the generated response requires further processing.

## Technology Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Agent orchestration | LangGraph |
| LLM integration | Google Gemini |
| Retrieval-Augmented Generation | FAISS, SQLite |
| Backend development | Python |
| Containerization | Docker, Docker Compose |
| Version control | Git, GitHub |

## Getting Started

### Prerequisites

- Python 3.13+
- Git
- Docker Desktop with Docker Compose
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/AI-Production-Support.git
cd AI-Production-Support
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username.

### 2. Configure Environment Variables

Create a `.env` file in the project root and configure the required values:

```dotenv
GOOGLE_API_KEY=your_gemini_api_key
MODEL_NAME=your_configured_gemini_model
```

Use the model name supported by your current project configuration.

**Security:** Never commit `.env` files, API keys, or other credentials to GitHub.

### 3. Build and Start the Application

From the project root, run:

```bash
docker compose build
docker compose up -d
```

### 4. Build the Knowledge Index

Run the indexing process inside the application container:

```bash
docker compose exec ai-production-support python -m src.indexing.indexer
```

Ensure the required knowledge-source files and configuration are available before indexing.

## Project Structure

The codebase is organized around separate responsibilities:

- `src/agents/` — agent responsibilities and reasoning stages
- `src/graph/` — workflow definition, state, nodes, and routing
- `src/retrieval/` — knowledge retrieval and related components
- `src/indexing/` — knowledge indexing pipeline
- `experiments/` — experiments and development utilities

Refer to the repository for the current implementation and supporting configuration.

## Development Roadmap

Planned enhancements include:

- API-based access to support workflows
- MCP-based tool integration
- Workflow tracing and evaluation
- Cloud deployment and operational hardening
- Expanded testing, monitoring, and reliability controls

## Project Status

This project is under active development, with a focus on applying enterprise-oriented AI engineering patterns to production support workflows. It is intended to demonstrate practical implementation of agent orchestration, retrieval pipelines, and evidence-grounded LLM applications.

