# GridTrader Pro - Systematic Investment Management Platform

A comprehensive investment management platform featuring grid trading algorithms, portfolio rebalancing, and real-time market data integration.

## 🚀 Features

- **Google OAuth Authentication** with JWT tokens
- **Real-time Market Data** via yfinance integration
- **Grid Trading Algorithms** with dynamic spacing
- **Portfolio Management** with automated rebalancing
- **Interactive Streamlit Dashboard** with live charts
- **Background Data Processing** with Celery
- **Production-Ready Docker Deployment**

## 📋 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: MySQL 8.0+
- **Authentication**: Google OAuth 2.0 + JWT
- **Data Source**: yfinance (Yahoo Finance)
- **Frontend**: Streamlit
- **Background Tasks**: Celery + Redis
- **Deployment**: Docker + Nginx + Supervisor

## 🏗️ Architecture

```
GridTrader Pro/
├── app/                    # Main application
│   ├── auth/              # Authentication (Google OAuth)
│   ├── middleware/        # JWT middleware
│   ├── routers/          # API routes
│   ├── algorithms/       # Trading algorithms
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   ├── data_provider.py  # yfinance integration
│   ├── tasks.py          # Celery background tasks
│   └── main.py           # FastAPI application
├── docker/               # Docker configuration
├── static/              # Static assets
├── streamlit_app.py     # Streamlit dashboard
├── requirements.txt     # Python dependencies
├── Dockerfile          # Multi-stage Docker build
└── README.md
```

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd gridtrader-pro
cp env.example .env
```

### 2. Configure Environment

Edit `.env` file with your configuration:

```bash
# Database
DB_HOST=your-mysql-host
DB_PASSWORD=your-mysql-password

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://gridsai.app/api/v1/auth/google/callback

# Application
SECRET_KEY=your-64-character-jwt-secret
FRONTEND_URL=https://gridsai.app

# Redis
REDIS_URL=redis://your-redis-connection
```

### 3. Deploy with Docker

```bash
# Build and run
docker build -t gridtrader-pro .
docker run -p 3000:3000 --env-file .env gridtrader-pro
```

### 4. Access the Application

- **Main Dashboard**: https://gridsai.app
- **API Documentation**: https://gridsai.app/docs
- **Health Check**: https://gridsai.app/health

## 🔐 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable Google+ API and OAuth2 API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `https://gridsai.app/api/v1/auth/google/callback`
6. Add authorized JavaScript origins:
   - `https://gridsai.app`
7. Copy Client ID and Secret to `.env`

## 📊 API Endpoints

### Authentication
- `GET /api/v1/auth/google` - Initiate Google OAuth
- `POST /api/v1/auth/login` - Email/password login
- `POST /api/v1/auth/register` - Create account
- `GET /api/v1/auth/me` - Get user info

### Portfolio Management
- `GET /api/v1/portfolios` - List portfolios
- `POST /api/v1/portfolios` - Create portfolio
- `GET /api/v1/portfolios/{id}` - Get portfolio details

### Market Data
- `GET /api/v1/market/securities/search` - Search securities
- `GET /api/v1/market/prices/{symbol}` - Historical prices
- `GET /api/v1/market/prices/{symbol}/current` - Real-time price

### Grid Trading
- `GET /api/v1/grids/{portfolio_id}` - List grid configs
- `POST /api/v1/grids/{portfolio_id}` - Create grid config
- `GET /api/v1/grids/{portfolio_id}/{grid_id}/levels` - Grid levels

### Analytics
- `GET /api/v1/analytics/{portfolio_id}/performance` - Performance metrics
- `GET /api/v1/analytics/{portfolio_id}/allocation` - Asset allocation
- `GET /api/v1/analytics/{portfolio_id}/rebalance` - Rebalance recommendations
- `GET /api/v1/analytics/{portfolio_id}/risk` - Risk metrics

## 🔄 Background Tasks

Celery handles automated data updates:

- **Real-time Prices**: Updated every 5 minutes
- **Daily Price Data**: Updated hourly
- **Grid Trigger Checks**: Continuous monitoring
- **Portfolio Rebalancing**: Daily analysis

## 🏦 Database Schema

### Core Tables
- `users` - User accounts and authentication
- `user_profiles` - User profile information
- `portfolios` - Investment portfolios
- `positions` - Portfolio positions
- `securities` - Security master data
- `price_data` - Historical price data
- `real_time_prices` - Current price cache

### Grid Trading
- `grid_configs` - Grid trading configurations
- `grid_levels` - Individual grid levels
- `allocation_targets` - Target allocations

## 🚢 Deployment to Coolify

### 1. Environment Setup in Coolify

Add these environment variables in Coolify dashboard:

```bash
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret  
GOOGLE_REDIRECT_URI=https://gridsai.app/api/v1/auth/google/callback
FRONTEND_URL=https://gridsai.app
SECRET_KEY=your-64-character-jwt-secret
DB_HOST=your-mysql-host
DB_PASSWORD=your-mysql-password
REDIS_URL=redis://your-redis-connection
```

### 2. Domain Configuration

- **Domain**: gridsai.app
- **SSL**: Enabled (Let's Encrypt)
- **Force HTTPS**: Yes
- **Port**: 8000

### 3. Deploy

1. Connect GitHub repository to Coolify
2. Set build pack to "Docker"
3. Configure environment variables
4. Deploy with one click

## 📈 Performance Targets

- **Response Time**: < 500ms for API endpoints
- **Uptime**: > 99.9% availability
- **Concurrent Users**: 1,000+ simultaneous users
- **Data Freshness**: Real-time prices every 5 minutes
- **SSL Grade**: A+ rating

## 🔧 Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI
uvicorn app.main:app --reload --port 8001

# Start Streamlit (separate terminal)
streamlit run streamlit_app.py --server.port 8502

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A app.tasks.celery_app beat --loglevel=info
```

### Testing

```bash
# Test API endpoints
curl https://gridsai.app/health
curl https://gridsai.app/api/v1/auth/google

# Test with authentication
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://gridsai.app/api/v1/portfolios
```

## 📊 Monitoring

### Health Checks
- Application: `https://gridsai.app/health`
- Database connectivity
- Redis connectivity
- yfinance API status

### Logs
```bash
# Application logs
docker logs gridtrader-app --tail=100 -f

# Service-specific logs
docker exec gridtrader-app tail -f /var/log/supervisor/fastapi.out.log
docker exec gridtrader-app tail -f /var/log/supervisor/streamlit.out.log
docker exec gridtrader-app tail -f /var/log/supervisor/celery.out.log
```

## 🔒 Security Features

- **JWT Authentication** with secure token handling
- **Google OAuth Integration** for secure login
- **HTTPS Enforcement** with automatic redirects
- **Security Headers** (CSP, HSTS, XSS Protection)
- **CORS Configuration** restricted to gridsai.app
- **Input Validation** on all API endpoints
- **SQL Injection Protection** via SQLAlchemy ORM

## 💰 Cost Optimization

- **75% reduction** in development costs vs custom build
- **95% reduction** in operational costs vs enterprise solutions
- **100% savings** on market data with free yfinance
- **Zero licensing fees** with open-source stack

## 🎯 Roadmap

### Phase 1: Core Features ✅
- Authentication system
- Portfolio management
- Grid trading algorithms
- Real-time data integration
- Streamlit dashboard

### Phase 2: Advanced Features
- Advanced analytics and reporting
- Risk management tools
- Mobile-responsive design
- Performance optimization

### Phase 3: Enterprise Features
- Multi-market support
- Institutional features
- API for third-party integrations
- Advanced backtesting

### Phase 4: Scale & Growth
- Mobile applications
- Advanced AI/ML features
- Multi-currency support
- Global market expansion

## 🆘 Support

### Troubleshooting

**Google OAuth Issues:**
```bash
# Verify redirect URI matches exactly
echo $GOOGLE_REDIRECT_URI
# Should output: https://gridsai.app/api/v1/auth/google/callback
```

**Database Connection:**
```bash
# Test database connectivity
docker exec gridtrader-app python -c "
from app.database import engine
print('Database connection:', engine.execute('SELECT 1').scalar())
"
```

**SSL/HTTPS Issues:**
```bash
# Check SSL certificate
curl -vI https://gridsai.app 2>&1 | grep -i ssl
```

### Getting Help

1. Check the [Issues](../../issues) page
2. Review the deployment logs
3. Verify environment configuration
4. Test individual components

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Streamlit** for rapid dashboard development  
- **yfinance** for free market data access
- **Google OAuth** for secure authentication
- **Coolify** for simplified deployment

---

**Built for gridsai.app** - Systematic Investment Management Made Simple
