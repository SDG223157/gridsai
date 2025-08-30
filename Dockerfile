# GridTrader Pro - COMPLETELY NEW DOCKERFILE
# NO CACHE VERSION - 2024-08-30
FROM python:3.11-slim

# Unique environment to break all caches
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV REBUILD_VERSION=2024-08-30-NUCLEAR
ENV CACHE_BUST=12345

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ default-libmysqlclient-dev pkg-config \
    curl redis-tools supervisor nginx netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

WORKDIR /app

# Copy and install Python requirements
COPY gridtrader-pro/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application
COPY gridtrader-pro/ /app/

# Setup directories and permissions
RUN mkdir -p /app/logs /var/log/supervisor /var/log/nginx && \
    chown -R appuser:appuser /app && \
    chmod +x /app/docker/start.sh && \
    chmod +x /app/simple_db_setup.py

# Copy configuration files
RUN cp /app/docker/supervisord.conf /etc/supervisor/conf.d/ && \
    cp /app/docker/nginx.conf /etc/nginx/sites-available/default && \
    cp /app/docker/start.sh /start.sh && \
    chmod +x /start.sh

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

USER root
CMD ["/start.sh"]
