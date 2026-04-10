from openenv.core.env_server import create_fastapi_app
from server.models import SQLAgentAction, SQLAgentObservation
from server.support_env_environment import SQLAnalystEnvironment
import uvicorn

# Create FastAPI app with OpenEnv
app = create_fastapi_app(SQLAnalystEnvironment, SQLAgentAction, SQLAgentObservation)

# Health check endpoints
@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# IMPORTANT: run app directly (no string path)
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
