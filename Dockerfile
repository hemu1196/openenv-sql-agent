FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip

 
RUN pip install --no-cache-dir fastapi uvicorn openenv-core

ENV PYTHONPATH=/app

# IMPORTANT: correct port
EXPOSE 8000

# Start server properly (no unnecessary delay needed)
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
