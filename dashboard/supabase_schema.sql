-- Run this in Supabase SQL Editor to enable persistent storage
-- Tables: sessions, user_data

-- Sessions (for auth persistence)
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    expiry BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expiry);

-- User data (uploaded data + metadata per user)
CREATE TABLE IF NOT EXISTS user_data (
    username TEXT PRIMARY KEY,
    data_csv TEXT,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS for security (optional - use service role key to bypass)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;

-- Subscriptions (Stripe tier per user)
CREATE TABLE IF NOT EXISTS subscriptions (
    username TEXT PRIMARY KEY,
    tier TEXT NOT NULL DEFAULT 'free',
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access" ON subscriptions FOR ALL USING (true);

-- Policy: service role can do anything
CREATE POLICY "Service role full access" ON sessions FOR ALL USING (true);
CREATE POLICY "Service role full access" ON user_data FOR ALL USING (true);
