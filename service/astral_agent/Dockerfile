# Astral Agent service image — build from monorepo root (COPY paths are root-relative).
# Do NOT set Railway Root Directory to /service/astral_agent.
# Single uvicorn worker; scale out with replicas. Do not copy src/.
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY service/astral_agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY service/astral_agent/ /app/

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
