# Multi-stage Dockerfile for Coolify deployment
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    redis-tools \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY gridtrader-pro/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration files first (from build context)
COPY gridtrader-pro/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY gridtrader-pro/docker/nginx.conf /etc/nginx/sites-available/default
COPY gridtrader-pro/docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Copy application code
COPY gridtrader-pro/ .
RUN chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/logs /var/log/supervisor /var/log/nginx \
    && chown -R appuser:appuser /app/logs \
    && chmod 755 /app/logs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Switch to root for supervisor
USER root

# Start command
CMD ["/app/start.sh"]
