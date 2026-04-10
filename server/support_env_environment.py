import os
import random
import uuid
import sqlite3
from typing import Optional

from models import SQLAgentAction, SQLAgentObservation, SQLAgentState
from .db_utils import setup_database, get_tasks
from openenv.core.env_server import Environment

class SQLAnalystEnvironment(Environment):
    """A SQL Data Analyst Environment for OpenEnv."""
    
    def __init__(self):
        self._state = SQLAgentState()
        self._conn: Optional[sqlite3.Connection] = None
        self._tasks = get_tasks()
        self._target_difficulty = "easy"
        self._target_answer = ""
        self._grader = None
        
        # Tracking rewards
        self._found_correct_table = False
        self._valid_query_executed = False

    def reset(self, config: dict = None, **kwargs) -> SQLAgentObservation:
        """Start a new episode with a fresh database."""
        if self._conn:
            self._conn.close()
        self._conn = setup_database()

        # Config lets us override the difficulty
        if config and "difficulty" in config:
            self._target_difficulty = config["difficulty"]
        elif os.getenv("SQL_DIFFICULTY"):
            self._target_difficulty = os.getenv("SQL_DIFFICULTY")
        else:
            self._target_difficulty = random.choice(["easy", "medium", "hard"])
            
        task = self._tasks.get(self._target_difficulty, self._tasks["easy"])
        self._target_answer = task["answer"]
        self._grader = task["grader"]

        self._state = SQLAgentState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            difficulty=self._target_difficulty,
            question=task["question"],
            max_steps=15
        )
        
        self._found_correct_table = False
        self._valid_query_executed = False

        return SQLAgentObservation(
            done=False,
            reward=0.0,
            feedback=f"New Task! Difficulty: {self._target_difficulty}. Question: {self._state.question}\n"
                     f"You can explore the SQLite database. Useful tip: You can query sqlite_master to find tables."
        )

    def step(self, action: SQLAgentAction, **kwargs) -> SQLAgentObservation:
        """Process a query or answer submission."""
        self._state.step_count += 1
        
        # Check step limit
        if self._state.step_count > self._state.max_steps:
             return SQLAgentObservation(
                done=True,
                reward=0.0,
                feedback=f"Maximum steps reached. You failed to answer. The correct answer was: {self._target_answer}."
            )

        if action.action_type.lower() == "submit":
            ans = action.content
            is_correct = self._grader(ans, self._target_answer)
            
            if is_correct:
                reward = 1.0
                if not self._valid_query_executed:
                    reward -= 0.1 # Small penalty for guessing
                feedback = "Correct! Well done."
            else:
                reward = 0.0
                feedback = f"Incorrect answer. You submitted: {ans}. Task failed."
                
            return SQLAgentObservation(
                done=True,
                reward=reward,
                feedback=feedback
            )

        # Default action_type is "query"
        query = action.content
        if not query or not str(query).strip():
             return SQLAgentObservation(
                done=False,
                reward=0.0,
                feedback="Error: Empty query."
             )
        
        try:
            cursor = self._conn.cursor()
            cursor.execute(query)
            
            # Identify if it was a data extraction
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            # Convert rows to dicts for observation
            data = []
            for row in rows[:50]: # Limit to 50 rows preventing massive payload
                data.append(dict(zip(columns, row)))
            
            feedback = "Query executed successfully."
            if len(rows) > 50:
                feedback += f" Returned {len(rows)} rows total (first 50 shown)."
                
            # Assign partial rewards
            reward = 0.0
            if not self._valid_query_executed:
                self._valid_query_executed = True
                reward += 0.05
                
            return SQLAgentObservation(
                done=False,
                reward=reward,
                feedback=feedback,
                rows_returned=len(rows),
                columns=columns,
                data=data
            )
        except Exception as e:
            return SQLAgentObservation(
                done=False,
                reward=-0.01, # slight penalty for syntax errors
                feedback=f"SQL Error: {str(e)}"
            )

    @property
    def state(self) -> SQLAgentState:
        return self._state
