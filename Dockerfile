FROM python:3.12-slim

# prevents pyc files from being copied to the container
ENV PYTHONDONTWRITEBYTECODE=1

# Ensures that python output is logged in the container's terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

HEALTHCHECK CMD ["curl", "--fail", "http://localhost:8000", "||", "exit 1"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]