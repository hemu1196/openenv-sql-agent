import os
import sys
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openenv.core.env_server import create_fastapi_app
from server.models import SQLAgentAction, SQLAgentObservation
from server.support_env_environment import SQLAnalystEnvironment

# Create FastAPI app
app = create_fastapi_app(SQLAnalystEnvironment, SQLAgentAction, SQLAgentObservation)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
