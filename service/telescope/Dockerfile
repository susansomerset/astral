# Astral Telescope service image.
# Memory limit and /dev/shm sizing are deploy concerns (AST-1727 / Railway).
# Local run: docker run --init --shm-size=1g -e TELESCOPE_BEARER_TOKEN=... -p 8080:8080 <image>
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the Telescope package — src/ must not exist in this image.
COPY service/telescope/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY service/telescope/ /app/

# Non-root (official image provides pwuser)
USER pwuser

EXPOSE 8080

# --init is expected via docker run / Railway (reap zombies). Single uvicorn worker = one pool.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
