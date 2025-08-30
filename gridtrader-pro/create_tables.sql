-- GridTrader Pro Database Schema
-- MySQL compatible table creation

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    google_id VARCHAR(255),
    auth_provider ENUM('local','google') DEFAULT 'local',
    is_email_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_email (email),
    UNIQUE KEY unique_google_id (google_id),
    KEY idx_email (email),
    KEY idx_google_id (google_id)
);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id CHAR(36) NOT NULL,
    display_name VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    risk_tolerance ENUM('conservative','moderate','aggressive') DEFAULT 'moderate',
    investment_experience VARCHAR(20) DEFAULT 'beginner',
    preferred_currency VARCHAR(10) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en',
    google_profile_data JSON,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS oauth_sessions (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    provider ENUM('local','google') NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP NULL,
    scope VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    KEY idx_user_provider (user_id, provider)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    strategy_type ENUM('grid_trading','core_satellite','balanced','growth') DEFAULT 'core_satellite',
    total_value DECIMAL(15,2) DEFAULT 0.00,
    cash_balance DECIMAL(15,2) DEFAULT 0.00,
    base_currency VARCHAR(10) DEFAULT 'USD',
    target_allocation JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    KEY idx_user_id (user_id),
    KEY idx_active (is_active)
);

CREATE TABLE IF NOT EXISTS securities (
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(200),
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    currency VARCHAR(10) DEFAULT 'USD',
    country VARCHAR(50),
    yfinance_info JSON,
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol),
    KEY idx_sector (sector),
    KEY idx_exchange (exchange),
    KEY idx_active (is_active)
);

CREATE TABLE IF NOT EXISTS positions (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    portfolio_id CHAR(36) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    asset_type ENUM('stock','etf','index','crypto') DEFAULT 'stock',
    quantity DECIMAL(15,6) DEFAULT 0.000000,
    avg_cost DECIMAL(12,6) DEFAULT 0.000000,
    current_price DECIMAL(12,6) DEFAULT 0.000000,
    market_value DECIMAL(15,2) DEFAULT 0.00,
    unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'USD',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_position (portfolio_id, symbol),
    KEY idx_portfolio_id (portfolio_id),
    KEY idx_symbol (symbol)
);

CREATE TABLE IF NOT EXISTS grid_configs (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    portfolio_id CHAR(36) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    grid_type ENUM('percentage','fixed') DEFAULT 'percentage',
    base_price DECIMAL(12,6) NOT NULL,
    grid_spacing DECIMAL(8,4) DEFAULT 5.0000,
    num_grids_up INTEGER DEFAULT 10,
    num_grids_down INTEGER DEFAULT 10,
    position_size DECIMAL(15,2) NOT NULL,
    total_investment DECIMAL(15,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    KEY idx_portfolio_id (portfolio_id),
    KEY idx_symbol (symbol),
    KEY idx_active (is_active)
);

CREATE TABLE IF NOT EXISTS grid_levels (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    grid_config_id CHAR(36) NOT NULL,
    level_number INTEGER NOT NULL,
    trigger_price DECIMAL(12,6) NOT NULL,
    target_allocation DECIMAL(5,2) NOT NULL,
    is_filled BOOLEAN DEFAULT FALSE,
    filled_price DECIMAL(12,6) NULL,
    filled_quantity DECIMAL(15,6) NULL,
    last_triggered TIMESTAMP NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (grid_config_id) REFERENCES grid_configs(id) ON DELETE CASCADE,
    KEY idx_grid_config (grid_config_id),
    KEY idx_trigger_price (trigger_price)
);

CREATE TABLE IF NOT EXISTS allocation_targets (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    portfolio_id CHAR(36) NOT NULL,
    category VARCHAR(50) DEFAULT 'individual',
    symbol VARCHAR(20),
    sector_name VARCHAR(50),
    target_percentage DECIMAL(5,2) NOT NULL,
    min_percentage DECIMAL(5,2) DEFAULT 0.00,
    max_percentage DECIMAL(5,2) DEFAULT 100.00,
    rebalance_band DECIMAL(5,2) DEFAULT 5.00,
    PRIMARY KEY (id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS price_data (
    id BIGINT AUTO_INCREMENT,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(12,6),
    high_price DECIMAL(12,6),
    low_price DECIMAL(12,6),
    close_price DECIMAL(12,6) NOT NULL,
    adj_close DECIMAL(12,6),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (symbol) REFERENCES securities(symbol) ON DELETE CASCADE,
    UNIQUE KEY unique_symbol_date (symbol, date),
    KEY idx_symbol (symbol),
    KEY idx_date (date)
);

CREATE TABLE IF NOT EXISTS real_time_prices (
    symbol VARCHAR(20) NOT NULL,
    current_price DECIMAL(12,6) NOT NULL,
    change_amount DECIMAL(12,6) DEFAULT 0.000000,
    change_percent DECIMAL(8,4) DEFAULT 0.0000,
    volume BIGINT DEFAULT 0,
    market_cap BIGINT,
    pe_ratio DECIMAL(8,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol),
    FOREIGN KEY (symbol) REFERENCES securities(symbol) ON DELETE CASCADE,
    KEY idx_last_updated (last_updated)
);

CREATE TABLE IF NOT EXISTS alerts (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    portfolio_id CHAR(36),
    alert_type ENUM('rebalance','risk_limit','grid_trigger','price_alert','system') NOT NULL,
    severity ENUM('low','medium','high','critical') DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    KEY idx_user_id (user_id),
    KEY idx_created_at (created_at),
    KEY idx_severity (severity)
);

-- Insert sample securities data
INSERT IGNORE INTO securities (symbol, name, currency, is_active) VALUES 
('AAPL', 'Apple Inc.', 'USD', TRUE),
('MSFT', 'Microsoft Corporation', 'USD', TRUE),
('GOOGL', 'Alphabet Inc.', 'USD', TRUE),
('AMZN', 'Amazon.com Inc.', 'USD', TRUE),
('TSLA', 'Tesla Inc.', 'USD', TRUE),
('SPY', 'SPDR S&P 500 ETF', 'USD', TRUE),
('QQQ', 'Invesco QQQ ETF', 'USD', TRUE);
