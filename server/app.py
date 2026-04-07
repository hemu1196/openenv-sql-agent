from openenv.core.env_server import create_fastapi_app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openenv.core.env_server import create_fastapi_app
from models import SQLAgentAction, SQLAgentObservation
from server.support_env_environment import SQLAnalystEnvironment
import uvicorn

app = create_fastapi_app(SQLAnalystEnvironment, SQLAgentAction, SQLAgentObservation)

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
