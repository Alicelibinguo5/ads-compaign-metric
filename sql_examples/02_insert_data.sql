
        -- Insert sample campaign events
        INSERT INTO campaign_events VALUES
        ('evt_001', 'user_001', 'camp_001', 'impression', 'ios', 
         TIMESTAMP '2024-01-01 10:00:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app"}', 
         TIMESTAMP '2024-01-01 10:00:01'),
        ('evt_002', 'user_001', 'camp_001', 'click', 'ios', 
         TIMESTAMP '2024-01-01 10:01:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app"}', 
         TIMESTAMP '2024-01-01 10:01:01'),
        ('evt_003', 'user_001', 'camp_001', 'conversion', 'ios', 
         TIMESTAMP '2024-01-01 10:05:00', 25.0, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app", "conversion_type": "purchase"}', 
         TIMESTAMP '2024-01-01 10:05:01');
        

        -- Insert sample user profiles
        INSERT INTO user_profiles VALUES
        ('user_001', 28, 'M', 'US', 'en', 'ios', 
         TIMESTAMP '2023-12-01 09:00:00', TIMESTAMP '2024-01-01 10:05:00', 
         125.0, 15, '{"preferred_categories": ["gaming", "tech"]}', 
         TIMESTAMP '2024-01-01 10:05:00');
        
