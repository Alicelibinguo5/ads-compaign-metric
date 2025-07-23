-- Setup sample campaign data for Superset visualization
-- Connect to PostgreSQL and run this script

-- Create campaign events table
CREATE TABLE IF NOT EXISTS campaign_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50),
    user_id VARCHAR(50),
    campaign_id VARCHAR(50),
    event_type VARCHAR(20),
    platform VARCHAR(20),
    timestamp TIMESTAMP,
    revenue DECIMAL(10,2),
    country VARCHAR(10),
    device_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create campaign metrics table (aggregated)
CREATE TABLE IF NOT EXISTS campaign_metrics (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50),
    date DATE,
    platform VARCHAR(20),
    impressions BIGINT,
    clicks BIGINT,
    conversions BIGINT,
    revenue DECIMAL(10,2),
    ctr DECIMAL(5,4),
    cvr DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample campaign events
INSERT INTO campaign_events (event_id, user_id, campaign_id, event_type, platform, timestamp, revenue, country, device_type) VALUES
('evt_001', 'user_001', 'camp_001', 'impression', 'ios', '2024-01-01 10:00:00', NULL, 'US', 'iPhone'),
('evt_002', 'user_001', 'camp_001', 'click', 'ios', '2024-01-01 10:01:00', NULL, 'US', 'iPhone'),
('evt_003', 'user_001', 'camp_001', 'conversion', 'ios', '2024-01-01 10:05:00', 25.00, 'US', 'iPhone'),
('evt_004', 'user_002', 'camp_001', 'impression', 'android', '2024-01-01 10:02:00', NULL, 'US', 'Samsung'),
('evt_005', 'user_002', 'camp_001', 'click', 'android', '2024-01-01 10:03:00', NULL, 'US', 'Samsung'),
('evt_006', 'user_003', 'camp_002', 'impression', 'ios', '2024-01-01 11:00:00', NULL, 'CA', 'iPhone'),
('evt_007', 'user_003', 'camp_002', 'click', 'ios', '2024-01-01 11:01:00', NULL, 'CA', 'iPhone'),
('evt_008', 'user_004', 'camp_002', 'impression', 'android', '2024-01-01 11:02:00', NULL, 'CA', 'Samsung'),
('evt_009', 'user_004', 'camp_002', 'conversion', 'android', '2024-01-01 11:05:00', 30.00, 'CA', 'Samsung'),
('evt_010', 'user_005', 'camp_003', 'impression', 'ios', '2024-01-01 12:00:00', NULL, 'UK', 'iPhone'),
('evt_011', 'user_005', 'camp_003', 'click', 'ios', '2024-01-01 12:01:00', NULL, 'UK', 'iPhone'),
('evt_012', 'user_005', 'camp_003', 'conversion', 'ios', '2024-01-01 12:05:00', 20.00, 'UK', 'iPhone');

-- Insert sample campaign metrics (aggregated data)
INSERT INTO campaign_metrics (campaign_id, date, platform, impressions, clicks, conversions, revenue, ctr, cvr) VALUES
('camp_001', '2024-01-01', 'ios', 1000, 150, 25, 625.00, 0.1500, 0.1667),
('camp_001', '2024-01-01', 'android', 800, 120, 20, 500.00, 0.1500, 0.1667),
('camp_001', '2024-01-02', 'ios', 1200, 180, 30, 750.00, 0.1500, 0.1667),
('camp_001', '2024-01-02', 'android', 900, 135, 22, 550.00, 0.1500, 0.1630),
('camp_002', '2024-01-01', 'ios', 600, 90, 15, 375.00, 0.1500, 0.1667),
('camp_002', '2024-01-01', 'android', 500, 75, 12, 300.00, 0.1500, 0.1600),
('camp_002', '2024-01-02', 'ios', 700, 105, 18, 450.00, 0.1500, 0.1714),
('camp_002', '2024-01-02', 'android', 550, 82, 13, 325.00, 0.1491, 0.1585),
('camp_003', '2024-01-01', 'ios', 400, 60, 10, 250.00, 0.1500, 0.1667),
('camp_003', '2024-01-01', 'android', 300, 45, 7, 175.00, 0.1500, 0.1556),
('camp_003', '2024-01-02', 'ios', 450, 67, 11, 275.00, 0.1489, 0.1642),
('camp_003', '2024-01-02', 'android', 350, 52, 8, 200.00, 0.1486, 0.1538);

-- Create indexes for better performance
CREATE INDEX idx_campaign_events_campaign_id ON campaign_events(campaign_id);
CREATE INDEX idx_campaign_events_date ON campaign_events(date);
CREATE INDEX idx_campaign_events_platform ON campaign_events(platform);
CREATE INDEX idx_campaign_metrics_campaign_id ON campaign_metrics(campaign_id);
CREATE INDEX idx_campaign_metrics_date ON campaign_metrics(date);

-- Verify data
SELECT 'campaign_events' as table_name, COUNT(*) as row_count FROM campaign_events
UNION ALL
SELECT 'campaign_metrics' as table_name, COUNT(*) as row_count FROM campaign_metrics; 