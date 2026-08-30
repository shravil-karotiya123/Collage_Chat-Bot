# Multi-stage Dockerfile for College Bot Backend (Render Deployment)
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Copy installed site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Expose port (Render automatically supplies PORT env var, defaults to 8000)
ENV PORT=8000
EXPOSE 8000

# Start production server using uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
