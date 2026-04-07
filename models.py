from typing import List, Optional, Dict, Any
from openenv.core.env_server import Action, Observation, State

class SQLAgentAction(Action):
    """Action to interact with the SQL environment.
    action_type: 'query' or 'submit'
    content: The SQL query to execute, or the final answer to submit.
    """
    action_type: str = "query"
    content: str

class SQLAgentObservation(Observation):
    """Observation returned after an action.
    Note: `done` and `reward` are inherited from Observation.
    """
    feedback: str # Output of the SQL query, or error message, or success message.
    rows_returned: Optional[int] = None
    columns: Optional[List[str]] = None
    # We serialize the data into string values so they can be JSON transferred easily
    data: Optional[List[Dict[str, Any]]] = None

class SQLAgentState(State):
    """Episode metadata.
    Note: `episode_id` and `step_count` are inherited from State.
    """
    difficulty: str = "easy"
    question: str = ""
    max_steps: int = 20
