# AI Customer Operations Agent

A production-style MVP for customer support operations with a FastAPI backend, PostgreSQL persistence, AI agent orchestration, knowledge retrieval, and evaluation tooling.

## Overview

This project demonstrates a practical support workflow for customer service teams:

- FastAPI API for health, ready checks, customers, orders, and agent interactions
- PostgreSQL-backed data model for customers, orders, support interactions, and knowledge docs
- Agentic orchestration with allowlisted tool execution and validation
- Mock-first LLM workflow with optional real OpenAI-compatible integrations
- Retrieval-augmented generation using chunking and embeddings
- Automated evaluation suite to measure workflow quality
- Docker Compose setup for local development and demo deployments

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 + PostgreSQL
- Pydantic + Pydantic Settings
- pytest + pytest-asyncio
- OpenAI Python SDK (optional, gated by configuration)
- Docker Compose

## Local setup

1. Create a Python virtual environment and install dependencies:
   - python -m venv .venv
   - . .venv/bin/activate
   - python -m pip install -r requirements.txt
2. Copy the example environment file:
   - cp .env.example .env
3. Start PostgreSQL and the API with Docker Compose:
   - docker compose up --build
4. Validate the app:
   - curl http://localhost:8000/api/health
   - curl http://localhost:8000/api/ready

## Runtime modes

The app supports a safe mock mode by default:

- LLM_PROVIDER=mock
- EMBEDDING_PROVIDER=mock

To enable real OpenAI-backed behavior, set the corresponding environment variables in your .env file:

- LLM_PROVIDER=openai
- EMBEDDING_PROVIDER=openai
- OPENAI_API_KEY=<your_key>
- OPENAI_MODEL=gpt-4o-mini
- OPENAI_EMBEDDING_MODEL=text-embedding-3-small

When a real provider is configured without a key, the app raises a configuration error instead of silently falling back to mock mode.

## APIs

Core routes are grouped under the application root and include:

- /api/health
- /api/ready
- /api/customers
- /api/orders
- /api/agent
- /api/evaluate
- /api/knowledge
- /api/interactions

## Testing and evaluation

Run the test suite:

- pytest -q

Run the evaluation script:

- python scripts/run_evaluation.py

## Project structure

- app/: FastAPI app, core config, database models, repositories, agents, LLM abstraction, and RAG components
- scripts/: database seeding and evaluation scripts
- tests/: regression coverage for health, orders, customers, agent behavior, tool validation, and RAG behavior

## Security notes

- Tool execution is allowlisted and validated before invocation.
- Provider selection is explicit and configuration-driven.
- Sensitive keys are not stored in source control; use a local .env file or a secure deployment secret store.
