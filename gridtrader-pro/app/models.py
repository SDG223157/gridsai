from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, Date, JSON, Enum, BigInteger, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid

class RiskTolerance(enum.Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"

class StrategyType(enum.Enum):
    grid_trading = "grid_trading"
    core_satellite = "core_satellite"
    balanced = "balanced"
    growth = "growth"

class AuthProvider(enum.Enum):
    local = "local"
    google = "google"

class Users(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.local)
    is_email_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    profile = relationship("UserProfiles", back_populates="user", uselist=False)
    portfolios = relationship("Portfolios", back_populates="user")
    alerts = relationship("Alerts", back_populates="user")
    oauth_sessions = relationship("OAuthSessions", back_populates="user")

class UserProfiles(Base):
    __tablename__ = "user_profiles"

    user_id = Column(CHAR(36), ForeignKey("users.id"), primary_key=True)
    display_name = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    risk_tolerance = Column(Enum(RiskTolerance), default=RiskTolerance.moderate)
    investment_experience = Column(String(20), default="beginner")
    preferred_currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en")
    google_profile_data = Column(JSON)

    user = relationship("Users", back_populates="profile")

class OAuthSessions(Base):
    __tablename__ = "oauth_sessions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(AuthProvider), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scope = Column(String(500))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("Users", back_populates="oauth_sessions")

class Portfolios(Base):
    __tablename__ = "portfolios"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    strategy_type = Column(Enum(StrategyType), default=StrategyType.core_satellite)
    total_value = Column(DECIMAL(15, 2), default=0.00)
    cash_balance = Column(DECIMAL(15, 2), default=0.00)
    base_currency = Column(String(10), default="USD")
    target_allocation = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("Users", back_populates="portfolios")
    positions = relationship("Positions", back_populates="portfolio")
    grid_configs = relationship("GridConfigs", back_populates="portfolio")
    allocation_targets = relationship("AllocationTargets", back_populates="portfolio")

class Positions(Base):
    __tablename__ = "positions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    asset_type = Column(String(20), default="stock")
    quantity = Column(DECIMAL(15, 6), default=0.000000)
    avg_cost = Column(DECIMAL(12, 6), default=0.000000)
    current_price = Column(DECIMAL(12, 6), default=0.000000)
    market_value = Column(DECIMAL(15, 2), default=0.00)
    unrealized_pnl = Column(DECIMAL(15, 2), default=0.00)
    currency = Column(String(10), default="USD")
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    portfolio = relationship("Portfolios", back_populates="positions")

class GridConfigs(Base):
    __tablename__ = "grid_configs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    grid_type = Column(String(20), default="percentage")
    base_price = Column(DECIMAL(12, 6), nullable=False)
    grid_spacing = Column(DECIMAL(8, 4), default=5.0000)
    num_grids_up = Column(Integer, default=10)
    num_grids_down = Column(Integer, default=10)
    position_size = Column(DECIMAL(15, 2), nullable=False)
    total_investment = Column(DECIMAL(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    portfolio = relationship("Portfolios", back_populates="grid_configs")
    grid_levels = relationship("GridLevels", back_populates="grid_config")

class GridLevels(Base):
    __tablename__ = "grid_levels"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grid_config_id = Column(CHAR(36), ForeignKey("grid_configs.id"), nullable=False)
    level_number = Column(Integer, nullable=False)
    trigger_price = Column(DECIMAL(12, 6), nullable=False)
    target_allocation = Column(DECIMAL(5, 2), nullable=False)
    is_filled = Column(Boolean, default=False)
    filled_price = Column(DECIMAL(12, 6), nullable=True)
    filled_quantity = Column(DECIMAL(15, 6), nullable=True)
    last_triggered = Column(DateTime, nullable=True)

    grid_config = relationship("GridConfigs", back_populates="grid_levels")

class AllocationTargets(Base):
    __tablename__ = "allocation_targets"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=False)
    category = Column(String(50), default="individual")
    symbol = Column(String(20))
    sector_name = Column(String(50))
    target_percentage = Column(DECIMAL(5, 2), nullable=False)
    min_percentage = Column(DECIMAL(5, 2), default=0.00)
    max_percentage = Column(DECIMAL(5, 2), default=100.00)
    rebalance_band = Column(DECIMAL(5, 2), default=5.00)

    portfolio = relationship("Portfolios", back_populates="allocation_targets")

class Securities(Base):
    __tablename__ = "securities"

    symbol = Column(String(20), primary_key=True)
    name = Column(String(200))
    exchange = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    currency = Column(String(10), default="USD")
    country = Column(String(50))
    yfinance_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class PriceData(Base):
    __tablename__ = "price_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("securities.symbol"), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(DECIMAL(12, 6))
    high_price = Column(DECIMAL(12, 6))
    low_price = Column(DECIMAL(12, 6))
    close_price = Column(DECIMAL(12, 6), nullable=False)
    adj_close = Column(DECIMAL(12, 6))
    volume = Column(BigInteger)
    created_at = Column(DateTime, server_default=func.current_timestamp())

class RealTimePrices(Base):
    __tablename__ = "real_time_prices"

    symbol = Column(String(20), ForeignKey("securities.symbol"), primary_key=True)
    current_price = Column(DECIMAL(12, 6), nullable=False)
    change_amount = Column(DECIMAL(12, 6), default=0.000000)
    change_percent = Column(DECIMAL(8, 4), default=0.0000)
    volume = Column(BigInteger, default=0)
    market_cap = Column(BigInteger)
    pe_ratio = Column(DECIMAL(8, 2))
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class Alerts(Base):
    __tablename__ = "alerts"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    title = Column(String(200), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    expires_at = Column(DateTime, nullable=True)

    user = relationship("Users", back_populates="alerts")
