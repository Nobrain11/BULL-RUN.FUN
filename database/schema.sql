CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    address VARCHAR(44) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    twitter VARCHAR(200),
    telegram VARCHAR(200),
    website VARCHAR(200),
    price NUMERIC(20, 10) DEFAULT 0.0,
    market_cap NUMERIC(20, 2) DEFAULT 0.0,
    volume_24h NUMERIC(20, 2) DEFAULT 0.0,
    baseline_mcap NUMERIC(20, 2) DEFAULT 0.0,
    current_multiplier NUMERIC(10, 4) DEFAULT 1.0,
    highest_multiplier NUMERIC(10, 4) DEFAULT 1.0,
    vote_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    is_sponsored BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    sponsor_position INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tokens_address ON tokens(address);
CREATE INDEX idx_tokens_status ON tokens(status);
CREATE INDEX idx_tokens_sponsored ON tokens(is_sponsored);
CREATE INDEX idx_tokens_multiplier ON tokens(current_multiplier DESC);
CREATE INDEX idx_tokens_created ON tokens(created_at DESC);

CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) NOT NULL REFERENCES tokens(address) ON DELETE CASCADE,
    multiplier NUMERIC(10, 4) NOT NULL,
    mcap_at_milestone NUMERIC(20, 2) NOT NULL,
    reached_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    alert_sent BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_milestones_token ON milestones(token_address);
CREATE INDEX idx_milestones_multiplier ON milestones(multiplier);

CREATE TABLE sponsored (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) NOT NULL REFERENCES tokens(address) ON DELETE CASCADE,
    package VARCHAR(20) NOT NULL,
    price NUMERIC(10, 4) NOT NULL,
    position INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    transaction_signature VARCHAR(100),
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sponsored_token ON sponsored(token_address);
CREATE INDEX idx_sponsored_user ON sponsored(user_id);
CREATE INDEX idx_sponsored_active ON sponsored(is_active);

CREATE TABLE listing_requests (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) NOT NULL,
    name VARCHAR(100),
    symbol VARCHAR(20),
    description TEXT,
    logo_url VARCHAR(500),
    twitter VARCHAR(200),
    telegram VARCHAR(200),
    website VARCHAR(200),
    submitted_by BIGINT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_listing_requests_address ON listing_requests(token_address);
CREATE INDEX idx_listing_requests_status ON listing_requests(status);
CREATE INDEX idx_listing_requests_created ON listing_requests(created_at DESC);

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) NOT NULL REFERENCES tokens(address) ON DELETE CASCADE,
    ip_address VARCHAR(45) NOT NULL,
    voted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(token_address, ip_address)
);

CREATE INDEX idx_votes_token ON votes(token_address);
CREATE INDEX idx_votes_ip ON votes(ip_address);

CREATE TABLE revenue (
    id SERIAL PRIMARY KEY,
    token_address VARCHAR(44) NOT NULL,
    user_id BIGINT NOT NULL,
    package VARCHAR(20) NOT NULL,
    amount NUMERIC(10, 4) NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    transaction_signature VARCHAR(100)
);

CREATE INDEX idx_revenue_token ON revenue(token_address);
CREATE INDEX idx_revenue_user ON revenue(user_id);
CREATE INDEX idx_revenue_paid ON revenue(paid_at DESC);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    wallet_address VARCHAR(44),
    total_spent NUMERIC(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_telegram ON users(user_id);

CREATE TABLE bot_sessions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    current_step VARCHAR(50) DEFAULT 'idle',
    current_token VARCHAR(44),
    temp_data JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bot_sessions_user ON bot_sessions(user_id);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tokens_updated_at
    BEFORE UPDATE ON tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
