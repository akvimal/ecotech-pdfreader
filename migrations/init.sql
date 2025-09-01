-- PDF Processor Application Database Schema
-- Version: 1.0.0
-- Date: 2024-12-01

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email accounts configuration
CREATE TABLE IF NOT EXISTS email_accounts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    server_type VARCHAR(20) DEFAULT 'imap' CHECK (server_type IN ('imap', 'exchange', 'pop3')),
    imap_server VARCHAR(255) NOT NULL,
    imap_port INTEGER DEFAULT 993,
    use_ssl BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL,
    password_encrypted TEXT NOT NULL, -- Encrypted password
    folder_to_monitor VARCHAR(100) DEFAULT 'INBOX',
    email_filter_rules JSONB DEFAULT '{}', -- Filter rules for emails
    last_checked TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, account_name)
);

-- PDF mapping rules
CREATE TABLE IF NOT EXISTS mapping_rules (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    pdf_patterns JSONB NOT NULL DEFAULT '{}', -- Table structure patterns
    excel_template JSONB NOT NULL DEFAULT '{}', -- Output format definition
    transformation_rules JSONB DEFAULT '{}', -- Data processing rules
    validation_rules JSONB DEFAULT '{}', -- Quality checks
    is_shared BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, rule_name)
);

-- Processing jobs/history
CREATE TABLE IF NOT EXISTS processing_jobs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_account_id INTEGER REFERENCES email_accounts(id) ON DELETE SET NULL,
    mapping_rule_id INTEGER REFERENCES mapping_rules(id) ON DELETE SET NULL,
    
    -- File information
    pdf_file_name VARCHAR(500),
    pdf_file_path VARCHAR(1000),
    pdf_file_size INTEGER,
    excel_file_name VARCHAR(500),
    excel_file_path VARCHAR(1000),
    
    -- Email information
    email_subject TEXT,
    email_sender VARCHAR(255),
    email_received_at TIMESTAMP,
    
    -- Processing information
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    error_details JSONB DEFAULT '{}',
    
    -- Processing metrics
    pages_processed INTEGER DEFAULT 0,
    tables_extracted INTEGER DEFAULT 0,
    rows_converted INTEGER DEFAULT 0,
    processing_time_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User notification settings
CREATE TABLE IF NOT EXISTS notification_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    desktop_notifications BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    email_on_success BOOLEAN DEFAULT TRUE,
    email_on_failure BOOLEAN DEFAULT TRUE,
    notification_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application settings (system-wide)
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions (for API authentication)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address INET
);

-- Audit log for tracking user actions
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_email_accounts_user_id ON email_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_email_accounts_active ON email_accounts(is_active);
CREATE INDEX IF NOT EXISTS idx_email_accounts_last_checked ON email_accounts(last_checked);

CREATE INDEX IF NOT EXISTS idx_mapping_rules_user_id ON mapping_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_mapping_rules_active ON mapping_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_mapping_rules_shared ON mapping_rules(is_shared);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_user_id ON processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_created_at ON processing_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_email_account ON processing_jobs(email_account_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_email_accounts_updated_at BEFORE UPDATE ON email_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mapping_rules_updated_at BEFORE UPDATE ON mapping_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_app_settings_updated_at BEFORE UPDATE ON app_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default application settings
INSERT INTO app_settings (key, value, description) VALUES
    ('app_version', '1.0.0', 'Application version'),
    ('max_file_size_mb', '100', 'Maximum PDF file size in MB'),
    ('max_concurrent_jobs', '5', 'Maximum concurrent processing jobs'),
    ('email_check_interval', '60', 'Email check interval in seconds'),
    ('default_excel_template', '{"sheet_name": "Processed_Data", "include_headers": true}', 'Default Excel template'),
    ('backup_retention_days', '30', 'Number of days to retain backup files')
ON CONFLICT (key) DO NOTHING;

-- Create default admin user (password: 'admin123' - should be changed immediately)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, role, first_name, last_name) VALUES
    ('admin', 'admin@pdfprocessor.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.12cNrKAyq', 'admin', 'System', 'Administrator')
ON CONFLICT (username) DO NOTHING;

-- Create default notification settings for admin user
INSERT INTO notification_settings (user_id, notification_email)
SELECT id, email FROM users WHERE username = 'admin'
ON CONFLICT (user_id) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW user_processing_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(pj.id) as total_jobs,
    COUNT(CASE WHEN pj.status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN pj.status = 'failed' THEN 1 END) as failed_jobs,
    COUNT(CASE WHEN pj.status = 'pending' THEN 1 END) as pending_jobs,
    COALESCE(AVG(CASE WHEN pj.status = 'completed' THEN pj.processing_time_seconds END), 0) as avg_processing_time,
    COALESCE(SUM(pj.pages_processed), 0) as total_pages_processed,
    COALESCE(SUM(pj.rows_converted), 0) as total_rows_converted
FROM users u
LEFT JOIN processing_jobs pj ON u.id = pj.user_id
GROUP BY u.id, u.username;

CREATE OR REPLACE VIEW recent_processing_activity AS
SELECT 
    pj.id,
    pj.uuid,
    u.username,
    pj.pdf_file_name,
    pj.excel_file_name,
    mr.rule_name,
    pj.status,
    pj.pages_processed,
    pj.rows_converted,
    pj.processing_time_seconds,
    pj.created_at,
    pj.completed_at,
    CASE 
        WHEN pj.completed_at IS NOT NULL THEN pj.completed_at
        ELSE pj.created_at 
    END as sort_date
FROM processing_jobs pj
JOIN users u ON pj.user_id = u.id
LEFT JOIN mapping_rules mr ON pj.mapping_rule_id = mr.id
ORDER BY sort_date DESC
LIMIT 100;

-- Function to clean old sessions
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS INTEGER AS $
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$ LANGUAGE plpgsql;

-- Function to get user statistics
CREATE OR REPLACE FUNCTION get_user_statistics(user_id_param INTEGER)
RETURNS TABLE(
    total_jobs INTEGER,
    completed_jobs INTEGER,
    failed_jobs INTEGER,
    success_rate DECIMAL,
    total_processing_time INTEGER,
    avg_processing_time DECIMAL,
    total_pages INTEGER,
    total_rows INTEGER
) AS $
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_jobs,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::INTEGER as completed_jobs,
        COUNT(CASE WHEN status = 'failed' THEN 1 END)::INTEGER as failed_jobs,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND((COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL) * 100, 2)
            ELSE 0.00 
        END as success_rate,
        COALESCE(SUM(processing_time_seconds), 0)::INTEGER as total_processing_time,
        COALESCE(AVG(CASE WHEN status = 'completed' THEN processing_time_seconds END), 0)::DECIMAL as avg_processing_time,
        COALESCE(SUM(pages_processed), 0)::INTEGER as total_pages,
        COALESCE(SUM(rows_converted), 0)::INTEGER as total_rows
    FROM processing_jobs 
    WHERE user_id = user_id_param;
END;
$ LANGUAGE plpgsql;

-- Grant permissions to application user (if different from postgres)
-- Note: In production, create a separate user with limited permissions
-- GRANT USAGE ON SCHEMA public TO pdf_processor_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pdf_processor_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pdf_processor_app;

COMMIT;