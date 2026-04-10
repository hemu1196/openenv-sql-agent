FROM python:3.10-slim

WORKDIR /app

COPY . .

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install required runtime deps explicitly (IMPORTANT)
RUN pip install --no-cache-dir fastapi uvicorn

# Install your project (if valid)
RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

EXPOSE 8000

# Add delay so server is ready before validator connects
CMD ["sh", "-c", "sleep 2 && uvicorn server.app:app --host 0.0.0.0 --port 8000"]