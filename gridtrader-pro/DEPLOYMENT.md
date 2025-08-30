# GridTrader Pro - Deployment Guide for gridsai.app

This guide provides step-by-step instructions to deploy GridTrader Pro to gridsai.app using Coolify.

## 🚀 Pre-Deployment Checklist

### 1. Google OAuth Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable APIs:
   - Google+ API
   - Google OAuth2 API
   - Google People API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Name: GridTrader Pro
   - Authorized JavaScript origins:
     - `https://gridsai.app`
     - `http://localhost:8000` (for development)
   - Authorized redirect URIs:
     - `https://gridsai.app/api/v1/auth/google/callback`
     - `http://localhost:8000/api/v1/auth/google/callback` (for development)
5. Copy Client ID and Client Secret

### 2. Database Setup

Set up MySQL 8.0+ database with:
- Database name: `gridtrader_db`
- User: `gridtrader` with full permissions
- Secure password

### 3. Redis Setup

Set up Redis instance for Celery background tasks.

## 📝 Environment Configuration

Create the following environment variables in Coolify:

```bash
# Database Configuration
DB_HOST=your-mysql-host.com
DB_PORT=3306
DB_NAME=gridtrader_db
DB_USER=gridtrader
DB_PASSWORD=your_secure_database_password

# Google OAuth Configuration  
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://gridsai.app/api/v1/auth/google/callback

# Application Configuration
SECRET_KEY=your_super_secret_jwt_key_at_least_32_characters_long
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=https://gridsai.app

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Redis Configuration
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://:your_redis_password@your-redis-host.com:6379/0

# External Services
WAIT_FOR_SERVICES=false
INIT_SAMPLE_DATA=true

# yfinance Configuration
YFINANCE_TIMEOUT=30
DATA_UPDATE_INTERVAL=300

# Logging & Monitoring
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

### Generate Secure Secret Key

```bash
# Generate a secure secret key
openssl rand -base64 64
```

## 🏗️ Coolify Deployment Steps

### 1. Create Application in Coolify

1. Login to your Coolify dashboard
2. Click "New Application"
3. Choose "Git Repository"
4. Connect your GitHub repository containing GridTrader Pro
5. Select the main branch

### 2. Configure Application Settings

- **Name**: gridtrader-pro
- **Build Pack**: Docker
- **Dockerfile Location**: `./Dockerfile`
- **Port**: 8000
- **Domain**: gridsai.app

### 3. Environment Variables

Add all environment variables listed above in the Coolify environment section.

### 4. Domain & SSL Configuration

- **Domain**: gridsai.app
- **SSL Certificate**: Enable Let's Encrypt
- **Force HTTPS**: Yes
- **WWW Redirect**: Optional (redirect www.gridsai.app to gridsai.app)

### 5. Deploy

Click "Deploy" button and monitor the build logs.

## ✅ Post-Deployment Verification

### 1. Health Check

```bash
curl https://gridsai.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "yfinance": "healthy"
  }
}
```

### 2. Google OAuth Test

```bash
curl -I https://gridsai.app/api/v1/auth/google
```

Should return HTTP 302 redirect to Google OAuth.

### 3. Streamlit Dashboard

Open https://gridsai.app in browser - should show login page.

### 4. API Documentation

Access https://gridsai.app/docs for Swagger UI.

## 🔧 Initial Data Setup

### 1. SSH into Container

```bash
# Get container ID
docker ps | grep gridtrader

# SSH into container
docker exec -it <container-id> bash
```

### 2. Initialize Sample Data

```bash
cd /app && python -c "
import asyncio
from app.data_provider import YFinanceDataProvider

async def init_data():
    provider = YFinanceDataProvider()
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ', 'VTI', 'META', 'NVDA']
    await provider.update_securities_database(symbols)
    await provider.update_price_data(symbols, period='1y')
    print('Sample data initialized successfully')

asyncio.run(init_data())
"
```

### 3. Verify Data

```bash
python -c "
from app.database import SessionLocal
from app.models import Securities, PriceData
db = SessionLocal()
securities_count = db.query(Securities).count()
price_count = db.query(PriceData).count()
print(f'Securities: {securities_count}, Price records: {price_count}')
db.close()
"
```

## 🔍 Monitoring & Maintenance

### 1. Application Logs

```bash
# View all logs
docker logs <container-id> --tail=100 -f

# View specific service logs
docker exec <container-id> tail -f /var/log/supervisor/fastapi.out.log
docker exec <container-id> tail -f /var/log/supervisor/streamlit.out.log
docker exec <container-id> tail -f /var/log/supervisor/celery.out.log
docker exec <container-id> tail -f /var/log/supervisor/nginx.out.log
```

### 2. Service Status

```bash
# Check all services
docker exec <container-id> supervisorctl status

# Restart specific service
docker exec <container-id> supervisorctl restart fastapi
```

### 3. Database Health

```bash
# Test database connection
docker exec <container-id> python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database connection: OK')
except Exception as e:
    print(f'Database error: {e}')
"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Google OAuth "redirect_uri_mismatch"

**Problem**: OAuth fails with redirect URI mismatch
**Solution**: 
- Verify `GOOGLE_REDIRECT_URI` exactly matches Google Console
- Ensure no trailing slashes
- Check case sensitivity

```bash
# Verify environment variable
docker exec <container-id> echo $GOOGLE_REDIRECT_URI
# Should output: https://gridsai.app/api/v1/auth/google/callback
```

#### 2. Database Connection Errors

**Problem**: Cannot connect to MySQL
**Solution**:
- Verify database credentials
- Check network connectivity
- Ensure database exists

```bash
# Test database connection
docker exec <container-id> python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='$DB_HOST',
        user='$DB_USER', 
        password='$DB_PASSWORD',
        database='$DB_NAME'
    )
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 3. Streamlit Not Loading

**Problem**: Main page shows error or doesn't load
**Solution**:
- Check Streamlit service status
- Verify nginx configuration
- Check port forwarding

```bash
# Check Streamlit service
docker exec <container-id> supervisorctl status streamlit

# Check nginx configuration
docker exec <container-id> nginx -t

# Restart services
docker exec <container-id> supervisorctl restart streamlit
docker exec <container-id> supervisorctl restart nginx
```

#### 4. SSL Certificate Issues

**Problem**: SSL certificate not working
**Solution**:
- Verify domain DNS points to server
- Check Coolify SSL configuration
- Wait for Let's Encrypt provisioning

```bash
# Check SSL certificate
curl -vI https://gridsai.app 2>&1 | grep -i ssl

# Check certificate expiry
openssl s_client -connect gridsai.app:443 -servername gridsai.app 2>/dev/null | openssl x509 -noout -dates
```

#### 5. Celery Tasks Not Running

**Problem**: Background tasks not executing
**Solution**:
- Check Redis connectivity
- Verify Celery worker status
- Check task scheduling

```bash
# Check Celery services
docker exec <container-id> supervisorctl status celery
docker exec <container-id> supervisorctl status celery-beat

# Test Redis connection
docker exec <container-id> redis-cli -u $REDIS_URL ping

# Check Celery logs
docker exec <container-id> tail -f /var/log/supervisor/celery.out.log
```

## 📊 Performance Monitoring

### 1. Key Metrics to Monitor

- **Response Time**: API endpoints < 500ms
- **Uptime**: > 99.9% availability
- **Memory Usage**: < 80% of allocated
- **CPU Usage**: < 70% average
- **Database Connections**: < 80% of pool

### 2. Health Check Endpoints

```bash
# Application health
curl https://gridsai.app/health

# API availability
curl https://gridsai.app/api/v1/auth/google

# Streamlit dashboard
curl -I https://gridsai.app/
```

### 3. Log Analysis

```bash
# Error patterns
docker exec <container-id> grep -i error /var/log/supervisor/*.log

# Performance issues
docker exec <container-id> grep -i "slow\|timeout" /var/log/supervisor/*.log

# Authentication issues
docker exec <container-id> grep -i "auth\|oauth" /var/log/supervisor/fastapi.out.log
```

## 🔄 Updates & Maintenance

### 1. Application Updates

1. Push code changes to GitHub
2. Coolify will auto-deploy if configured
3. Or manually trigger deployment in Coolify dashboard

### 2. Database Migrations

```bash
# Run migrations after code updates
docker exec <container-id> python -c "
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database migration completed')
"
```

### 3. Backup Strategy

```bash
# Database backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD gridtrader_db > backup_$(date +%Y%m%d).sql

# Application logs backup
docker exec <container-id> tar -czf logs_backup_$(date +%Y%m%d).tar.gz /app/logs
```

## 🎯 Success Metrics

After successful deployment, you should achieve:

- **✅ SSL A+ Rating**: Test at [SSL Labs](https://www.ssllabs.com/ssltest/)
- **✅ 99.9%+ Uptime**: Monitor with UptimeRobot or similar
- **✅ < 500ms Response Time**: For all API endpoints
- **✅ Google OAuth Working**: Users can sign in with Google
- **✅ Real-time Data**: Market data updates every 5 minutes
- **✅ Background Tasks**: Celery processing data updates

## 📞 Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review Coolify deployment logs
3. Verify all environment variables
4. Test individual components
5. Check Google OAuth configuration

---

**Deployment Target**: https://gridsai.app  
**Expected Deployment Time**: 10-15 minutes  
**Post-Setup Time**: 30 minutes including OAuth and data initialization
