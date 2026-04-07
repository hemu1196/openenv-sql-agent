from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import SQLAgentAction, SQLAgentObservation, SQLAgentState

class SQLAgentEnv(EnvClient[SQLAgentAction, SQLAgentObservation, SQLAgentState]):
    def _step_payload(self, action: SQLAgentAction) -> dict:
        return {"action_type": action.action_type, "content": action.content}

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})
        return StepResult(
            observation=SQLAgentObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                feedback=obs_data.get("feedback", ""),
                rows_returned=obs_data.get("rows_returned"),
                columns=obs_data.get("columns", []),
                data=obs_data.get("data", [])
            ),
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> SQLAgentState:
        return SQLAgentState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            difficulty=payload.get("difficulty", "easy"),
            question=payload.get("question", ""),
            max_steps=payload.get("max_steps", 15)
        )
