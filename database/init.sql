-- SME-Pulse AI - Database Initialization Script
-- Creates initial database schema and seed data

-- Create enum types (if not using SQLAlchemy enums)
DO $$ BEGIN
    CREATE TYPE document_type AS ENUM (
        'bank_statement', 
        'tally_export', 
        'zoho_export', 
        'gst_return', 
        'financial_report'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE industry_type AS ENUM (
        'manufacturing', 
        'trading', 
        'services', 
        'construction', 
        'healthcare', 
        'it_services', 
        'retail', 
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM (
        'low', 
        'medium', 
        'high', 
        'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create tables (indexes will be created separately for clarity)

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    phone VARCHAR(20),
    industry industry_type,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    industry industry_type,
    registration_number VARCHAR(50),
    gst_number VARCHAR(20),
    pan_number VARCHAR(20),
    address TEXT,
    monthly_revenue_estimate DOUBLE PRECISION,
    employee_count INTEGER,
    years_in_business INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    document_type document_type,
    mime_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,
    extracted_data JSONB,
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    statement_period_start TIMESTAMP,
    statement_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    date TIMESTAMP NOT NULL,
    description VARCHAR(500),
    amount DOUBLE PRECISION NOT NULL,
    transaction_type VARCHAR(20),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    is_flagged BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(100),
    counterparty VARCHAR(255),
    reference_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial metrics table
CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    period_type VARCHAR(20),
    
    -- Cash Flow Metrics
    total_inflows DOUBLE PRECISION DEFAULT 0,
    total_outflows DOUBLE PRECISION DEFAULT 0,
    net_cash_flow DOUBLE PRECISION DEFAULT 0,
    opening_balance DOUBLE PRECISION DEFAULT 0,
    closing_balance DOUBLE PRECISION DEFAULT 0,
    
    -- Liquidity Ratios
    current_ratio DOUBLE PRECISION,
    quick_ratio DOUBLE PRECISION,
    cash_ratio DOUBLE PRECISION,
    
    -- Leverage Ratios
    debt_to_equity DOUBLE PRECISION,
    debt_to_assets DOUBLE PRECISION,
    interest_coverage_ratio DOUBLE PRECISION,
    
    -- Efficiency Ratios
    receivables_turnover DOUBLE PRECISION,
    payables_turnover DOUBLE PRECISION,
    inventory_turnover DOUBLE PRECISION,
    
    -- Profitability Margins
    gross_margin DOUBLE PRECISION,
    operating_margin DOUBLE PRECISION,
    net_margin DOUBLE PRECISION,
    return_on_assets DOUBLE PRECISION,
    return_on_equity DOUBLE PRECISION,
    
    -- DSCR
    dscr DOUBLE PRECISION,
    annual_debt_service DOUBLE PRECISION,
    annual_net_operating_income DOUBLE PRECISION,
    
    -- Raw data snapshot
    raw_data JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health scores table
CREATE TABLE IF NOT EXISTS health_scores (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    overall_score DOUBLE PRECISION NOT NULL,
    previous_score DOUBLE PRECISION,
    score_change DOUBLE PRECISION,
    
    -- Component Scores
    cash_flow_score DOUBLE PRECISION,
    profitability_score DOUBLE PRECISION,
    leverage_score DOUBLE PRECISION,
    efficiency_score DOUBLE PRECISION,
    stability_score DOUBLE PRECISION,
    
    -- Risk Assessment
    risk_level risk_level,
    risk_factors JSONB,
    credit_rating VARCHAR(20),
    
    -- AI Narrative
    narrative_summary TEXT,
    recommendations JSONB,
    
    -- Period
    assessment_period_start TIMESTAMP,
    assessment_period_end TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    transaction_id INTEGER REFERENCES transactions(id),
    anomaly_type VARCHAR(100) NOT NULL,
    severity risk_level NOT NULL,
    description TEXT NOT NULL,
    details JSONB,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    category VARCHAR(100),
    priority INTEGER,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    potential_impact TEXT,
    implementation_steps JSONB,
    is_implemented BOOLEAN DEFAULT FALSE,
    implemented_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    ip_address VARCHAR(50),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_companies_user ON companies(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_status ON documents(user_id, status);
CREATE INDEX IF NOT EXISTS idx_documents_company_type ON documents(company_id, document_type);
CREATE INDEX IF NOT EXISTS idx_transactions_document_date ON transactions(document_id, date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_flagged ON transactions(is_flagged);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_company_period ON financial_metrics(company_id, period_start);
CREATE INDEX IF NOT EXISTS idx_health_score_company_date ON health_scores(company_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_created ON audit_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_created ON audit_logs(action, created_at);

-- Insert sample data for testing (demo purposes)
INSERT INTO users (email, hashed_password, full_name, company_name, phone, industry, consent_given, consent_timestamp)
VALUES 
    ('demo@sme-pulse.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.RC7N8y6a.dJGq', 'Demo User', 'Sample Manufacturing Pvt Ltd', '+91-9876543210', 'manufacturing', TRUE, CURRENT_TIMESTAMP),
    ('admin@sme-pulse.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.RC7N8y6a.dJGq', 'Admin User', 'Admin Company', '+91-9876543211', 'services', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (email) DO NOTHING;

-- Sample company for demo user
INSERT INTO companies (user_id, name, industry, registration_number, gst_number, monthly_revenue_estimate, employee_count, years_in_business)
SELECT id, 'Sample Manufacturing Pvt Ltd', 'manufacturing', 'U12345MH2020', '27ABCDE1234F1Z5', 5000000, 50, 5
FROM users WHERE email = 'demo@sme-pulse.ai'
ON CONFLICT DO NOTHING;

-- Sample health score for demo company
INSERT INTO health_scores (company_id, overall_score, cash_flow_score, profitability_score, leverage_score, efficiency_score, stability_score, risk_level, credit_rating, narrative_summary, assessment_period_start, assessment_period_end)
SELECT 
    c.id, 
    72.5,  -- overall score
    78.0,  -- cash flow
    68.0,  -- profitability
    75.0,  -- leverage
    70.0,  -- efficiency
    65.0,  -- stability
    'medium',
    'BBB',
    'The company demonstrates healthy financial performance with strong cash flow generation. Profitability metrics are above industry average, though there is room for improvement in operational efficiency. The leverage position is conservative, providing adequate buffer for growth. Overall, the company is well-positioned for expansion.',
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE
FROM companies c
WHERE c.name = 'Sample Manufacturing Pvt Ltd'
ON CONFLICT DO NOTHING;

-- Add sample financial metrics
INSERT INTO financial_metrics (company_id, period_start, period_end, period_type, total_inflows, total_outflows, net_cash_flow, current_ratio, quick_ratio, debt_to_equity, gross_margin, net_margin, dscr)
SELECT 
    c.id,
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE,
    'quarterly',
    15000000,  -- total inflows
    12500000,  -- total outflows
    2500000,   -- net cash flow
    1.45,      -- current ratio
    1.10,      -- quick ratio
    0.45,      -- debt to equity
    68.5,      -- gross margin
    12.5,      -- net margin
    1.85       -- DSCR
FROM companies c
WHERE c.name = 'Sample Manufacturing Pvt Ltd'
ON CONFLICT DO NOTHING;

-- Sample anomalies
INSERT INTO anomalies (company_id, anomaly_type, severity, description, details)
SELECT 
    c.id,
    'large_transaction',
    'medium',
    'Unusually large transaction detected',
    '{"amount": 500000, "average_transaction": 50000, "threshold": 250000}'
FROM companies c
WHERE c.name = 'Sample Manufacturing Pvt Ltd'
ON CONFLICT DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sme_pulse_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sme_pulse_user;

-- Comment on tables
COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON TABLE companies IS 'Company/SME profiles';
COMMENT ON TABLE documents IS 'Uploaded financial documents';
COMMENT ON TABLE transactions IS 'Extracted financial transactions';
COMMENT ON TABLE financial_metrics IS 'Calculated financial ratios and metrics';
COMMENT ON TABLE health_scores IS 'AI-calculated health scores and assessments';
COMMENT ON TABLE anomalies IS 'Detected financial anomalies and irregularities';
COMMENT ON TABLE recommendations IS 'AI-generated financial recommendations';
COMMENT ON TABLE audit_logs IS 'Audit trail for compliance and security';

