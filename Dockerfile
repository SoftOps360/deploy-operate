# Small, reproducible image for the ask-runbook service.
FROM python:3.11-slim

# Don't write .pyc, and stream logs (so `docker logs` shows output immediately).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first so this layer caches unless requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the app.
COPY . .

# Run as a non-root user (least privilege).
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# The GROQ_API_KEY is provided at runtime (compose / -e), NOT baked into the image.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
