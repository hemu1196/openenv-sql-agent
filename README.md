---
title: support-env
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
---
# OpenEnv SQL Data Analyst

An OpenEnv compatible environment that simulates an AI Agent acting as a SQL Data Analyst. The agent must navigate an SQLite database structure to answer direct business questions over synthetic data across multiple tables.

## Motivation
Data analysis and answering business queries using a relational database is a prevalent industrial problem. Evaluation using Text2SQL often considers simply parsing SQL correctness. Building a multi-turn OpenEnv environment ensures agents aren't just trained to execute one-shot queries, but to logically explore unknown databases, identify joining constraints, query the structure, iteratively fix errors, and report a finalized answer.

## Action Space
The `SQLAgentAction` includes two variables:
- `action_type`: Can either be `query` (to execute raw SQL to database limit 50 rows) or `submit` (to submit the final answer output).
- `content`: Holds the raw query or the raw English-based answer text.

## Observation Space
The `SQLAgentObservation` gives a structured text representation via:
- `feedback`: Explains any generated SQL errors, success notes, or instructions.
- `rows_returned`: An integer of total rows returned.
- `columns`: A list of strings identifying returned schema properties.
- `data`: A structured JSON list mapping the SQL return set.

## 3 Task Levels
- **Easy**: Isolate a direct value from a single table matching a specific parameter.
- **Medium**: Leverage a simple table `JOIN` mapping to perform standard counting/aggregations (e.g. Total Revenue).
- **Hard**: Perform higher complexity grouping and joining logic requiring deep linking through the multi-table schema.

## Evaluation & Reward
Maximum reward spans to `1.0`. 
Rewards are granted on:
- Exploring and writing a valid SQL statement (+0.05).
- Supplying the correct answer matching the strict programmatic grader logic.

## Usage Instructions
Using standard OpenEnv methodology:

```python
from client import SQLAgentEnv, SQLAgentAction
import asyncio

async def test():
    # Will connect automatically mapping the OpenEnv HF schema Space URL.
    env = SQLAgentEnv(base_url="http://localhost:8000")
    await env.connect()
    
    # 1. Reset
    result = await env.reset()
    
    # 2. Step 
    result = await env.step(SQLAgentAction(action_type="query", content="SELECT * FROM sqlite_master;"))
    print(result.observation.feedback)
    
    # 3. Complete
    result = await env.step(SQLAgentAction(action_type="submit", content="Diana Prince"))
    print(result.reward)
    
asyncio.run(test())
```

## Baseline Validation
The root `inference.py` script leverages a parameterized `OpenAI` client (which can wrap HuggingFace models using v1 compatibility paths) reading strictly tracked `[START]`, `[STEP]`, and `[END]` stdout. Run using Python directly to generate results.
