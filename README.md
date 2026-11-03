# ai-engineer-roadmap

Moving from analytics engineering into AI engineering, in the open. One study block a day,
each one ends with code that ran, and the shared parts are tested.

The plan has six parts. Each part ends with a project that has to run from a clean checkout.

| Part | Days | What it builds |
|---|---|---|
| 1. Foundations | 001–030 | Python for AI work, how LLMs behave, structured output, a first classifier |
| 2. Evals | 031–050 | Datasets, metrics, LLM-as-judge, an eval harness every later project uses |
| 3. Retrieval and RAG | 051–085 | Embeddings, hybrid search, reranking, answers with citations, measured |
| 4. Tools, agents, MCP | 086–110 | Tool calling, an agent loop with limits, an MCP server, agent evals |
| 5. Production | 111–145 | FastAPI service, Docker, tracing, cost control, safety, CI with an eval gate |
| 6. Middle level | 146–180 | Local inference, fine-tuning against a baseline, system design |

## Run it

```bash
uv sync                 # creates .venv from uv.lock
uv run pytest           # tests for src/aieng
uv run ruff check .     # lint
cp .env.example .env    # only when a lesson needs a model
```

## Layout

```
src/aieng/   code that more than one lesson uses — tested
lessons/     one script per study day: day_001.py, day_014-016.py
tests/       pytest
data/        small committed fixtures; raw dumps and indexes are git-ignored
```

Models are local first (Ollama), hosted free tiers second. No lesson needs a paid key.
