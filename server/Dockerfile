FROM python:3.10-slim

WORKDIR /app

RUN pip install openenv-core>=0.2.2 fastapi uvicorn pydantic openai

# Copy the server directory contents into /app/server
COPY . /app/server/

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
