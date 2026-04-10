FROM python:3.10-slim

WORKDIR /app

COPY . .

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install required runtime deps
RUN pip install --no-cache-dir fastapi uvicorn

# Install your project
RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

# IMPORTANT: correct port
EXPOSE 8000

# Start server properly (no unnecessary delay needed)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
