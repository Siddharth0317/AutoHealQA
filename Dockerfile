# Multi-stage Production Dockerfile for AutoHealQA Backend Engine
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python requirements and Playwright browsers (Chromium, Firefox, WebKit)
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium firefox webkit --with-deps

# Copy project source code
COPY backend ./backend
COPY executor ./executor
COPY agents ./agents
COPY storage ./storage

# Create artifacts directory
RUN mkdir -p storage/artifacts

# Expose backend API port
EXPOSE 8000

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8000

# Launch Uvicorn server
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
