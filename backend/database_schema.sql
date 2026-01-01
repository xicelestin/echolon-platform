-- Multi-Tenant OAuth Database Schema for Echolon Platform
-- PostgreSQL schema for storing tenant OAuth credentials and sync state

-- Tenants (Organizations/Companies using Echolon)
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    tenant_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,  -- e.g. acme-corp.echolon.ai
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50) DEFAULT 'free',  -- free, starter, pro, enterprise
    
    -- PropelAuth or Auth0 user ID of primary account owner
    owner_user_id VARCHAR(255) NOT NULL,
    
    -- Contact info
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    
    CONSTRAINT valid_subdomain CHECK (subdomain ~* '^[a-z0-9-]+$')
);

CREATE INDEX idx_tenants_uuid ON tenants(tenant_uuid);
CREATE INDEX idx_tenants_owner ON tenants(owner_user_id);


-- Connected Integrations (OAuth tokens per tenant per provider)
CREATE TABLE IF NOT EXISTS connected_integrations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Provider info
    provider VARCHAR(50) NOT NULL,  -- 'shopify', 'quickbooks', 'stripe', 'google_sheets'
    provider_account_id VARCHAR(255),  -- Shop domain, QB company ID, Stripe account ID
    provider_account_name VARCHAR(255),  -- Display name
    
    -- OAuth tokens (ENCRYPTED - use pgcrypto or application-level encryption)
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(50) DEFAULT 'Bearer',
    scopes TEXT[],  -- Array of granted scopes
    expires_at TIMESTAMP,
    
    -- Connection metadata
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending',  -- pending, syncing, success, error
    sync_error TEXT,
    
    -- Provider-specific metadata (JSONB for flexibility)
    metadata JSONB DEFAULT '{}'::jsonb,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT unique_tenant_provider UNIQUE(tenant_id, provider, provider_account_id)
);

CREATE INDEX idx_integrations_tenant ON connected_integrations(tenant_id);
CREATE INDEX idx_integrations_provider ON connected_integrations(provider);
CREATE INDEX idx_integrations_active ON connected_integrations(tenant_id, is_active);


-- Sync Jobs (Background data synchronization tracking)
CREATE TABLE IF NOT EXISTS sync_jobs (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES connected_integrations(id) ON DELETE CASCADE,
    
    job_type VARCHAR(50) NOT NULL,  -- 'full_sync', 'incremental', 'manual'
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Sync results
    records_fetched INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata
    sync_params JSONB DEFAULT '{}'::jsonb,  -- Date ranges, filters, etc.
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_sync_jobs_integration ON sync_jobs(integration_id);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status, started_at);


-- API Rate Limits (Track usage per provider to avoid hitting limits)
CREATE TABLE IF NOT EXISTS api_rate_limits (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES connected_integrations(id) ON DELETE CASCADE,
    
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    
    requests_made INTEGER DEFAULT 0,
    requests_limit INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_window UNIQUE(integration_id, window_start)
);

CREATE INDEX idx_rate_limits_window ON api_rate_limits(integration_id, window_start);


-- Audit Log (Security & compliance - who connected/disconnected what)
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE SET NULL,
    user_id VARCHAR(255),  -- PropelAuth/Auth0 user ID
    
    action VARCHAR(100) NOT NULL,  -- 'integration_connected', 'integration_disconnected', 'sync_triggered'
    resource_type VARCHAR(50),  -- 'integration', 'sync_job', 'settings'
    resource_id INTEGER,
    
    ip_address INET,
    user_agent TEXT,
    
    details JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);


-- OAuth State (For CSRF protection during OAuth flows)
CREATE TABLE IF NOT EXISTS oauth_states (
    state_token VARCHAR(255) PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    
    provider VARCHAR(50) NOT NULL,
    redirect_after VARCHAR(500),  -- Where to redirect user after OAuth completes
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_oauth_states_expiry ON oauth_states(expires_at) WHERE NOT used;


-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on tenants
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Views for common queries

-- Active integrations per tenant
CREATE OR REPLACE VIEW v_active_integrations AS
SELECT 
    t.tenant_uuid,
    t.company_name,
    ci.provider,
    ci.provider_account_name,
    ci.connected_at,
    ci.last_synced_at,
    ci.sync_status
FROM tenants t
JOIN connected_integrations ci ON t.id = ci.tenant_id
WHERE ci.is_active = TRUE AND t.is_active = TRUE;


-- Recent sync status per tenant
CREATE OR REPLACE VIEW v_recent_syncs AS
SELECT 
    t.tenant_uuid,
    ci.provider,
    sj.job_type,
    sj.status,
    sj.started_at,
    sj.completed_at,
    sj.records_processed,
    sj.error_message
FROM sync_jobs sj
JOIN connected_integrations ci ON sj.integration_id = ci.id
JOIN tenants t ON ci.tenant_id = t.id
ORDER BY sj.started_at DESC;


-- Comments for documentation
COMMENT ON TABLE tenants IS 'Organizations/companies using Echolon platform';
COMMENT ON TABLE connected_integrations IS 'OAuth credentials for external data sources (Shopify, QuickBooks, etc.)';
COMMENT ON TABLE sync_jobs IS 'Background jobs that fetch data from integrated services';
COMMENT ON TABLE api_rate_limits IS 'Track API usage to avoid hitting provider rate limits';
COMMENT ON TABLE audit_logs IS 'Security audit trail for all integration and sync actions';
COMMENT ON TABLE oauth_states IS 'Temporary CSRF tokens for OAuth flows';

COMMENT ON COLUMN connected_integrations.access_token IS 'MUST be encrypted at rest using pgcrypto or app-level encryption';
COMMENT ON COLUMN connected_integrations.refresh_token IS 'MUST be encrypted at rest using pgcrypto or app-level encryption';
