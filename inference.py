import asyncio
import os
import textwrap
import json
from typing import List, Optional

from openai import OpenAI
from client import SQLAgentEnv, SQLAgentAction

IMAGE_NAME = os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("MY_ENV_TASK", "sql-exploration")
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "openenv-sql-data-analyst")
MAX_STEPS = 10

SYSTEM_PROMPT = textwrap.dedent("""
    You are a SQL Data Analyst.
    Your goal is to answer business questions by querying an SQLite database.
    You can take two types of actions:
    1. SQL Query: `query: SELECT * FROM sqlite_master`
    2. Final Answer Submission: `submit: The answer is 42`
    
    You must output exactly one action per turn.
    Example:
    query: SELECT name FROM sqlite_master
""").strip()

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action!r} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def parse_model_response(response: str) -> SQLAgentAction:
    lines = response.strip().split("\n")
    for line in lines:
        if line.lower().startswith("query:"):
            return SQLAgentAction(action_type="query", content=line[6:].strip())
        if line.lower().startswith("submit:"):
            return SQLAgentAction(action_type="submit", content=line[7:].strip())
    # Default to querying if format is weird
    return SQLAgentAction(action_type="query", content=response.strip())

async def run_episode(client: OpenAI, env: SQLAgentEnv, difficulty: str):
    # Pass difficulty to server via env var for this run
    os.environ["SQL_DIFFICULTY"] = difficulty
    result = await env.reset()
    
    obs = result.observation
    rewards = []
    steps_taken = 0
    score = 0.0
    
    for step in range(1, MAX_STEPS + 1):
        if result.done:
            break
            
        user_prompt = f"Previous Feedback:\n{obs.feedback}\n"
        if getattr(obs, "data", None):
            user_prompt += f"Data: {json.dumps(obs.data[:5])}\n"
        user_prompt += "\nWhat is your next action?"
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=200,
                stream=False,
            )
            text = (completion.choices[0].message.content or "query: SELECT * FROM sqlite_master").strip()
        except BaseException as exc:
            text = "query: SELECT * FROM sqlite_master"
            error_val = str(exc)
            
        action = parse_model_response(text)
        result = await env.step(action)
        obs = result.observation
        reward = result.reward or 0.0
        done = result.done
        
        rewards.append(reward)
        steps_taken = step
        
        # Build action string without internal newlines so formatting complies
        action_str = f"{action.action_type}({str(action.content).strip()})"
        log_step(step=step, action=action_str, reward=reward, done=done, error=None)
        
        if done:
            break
            
    total_reward = sum(rewards)
    score = (total_reward / 1.0) if 1.0 > 0 else 0.0 # Our max possible theoretic reward varies but is ~1.0
    score = min(max(score, 0.0), 1.0)
    success = score >= 0.8
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Setup our environment connection
    try:
        if IMAGE_NAME:
            env = await SQLAgentEnv.from_docker_image(IMAGE_NAME)
        else:
            env = SQLAgentEnv(base_url=os.getenv("SERVER_URL", "http://localhost:8000"))
            await env.connect()
            
        log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
        for diff in ["easy", "medium", "hard"]:
            await run_episode(client, env, diff)
            
    finally:
        try:
            if 'env' in locals():
                await env.close()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
