
        -- Query 1: Basic campaign metrics
        SELECT 
            campaign_id,
            platform,
            COUNT(*) as total_events,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) as impressions,
            SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
            SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions,
            SUM(revenue) as total_revenue
        FROM campaign_events
        GROUP BY campaign_id, platform
        ORDER BY campaign_id, platform;
        

        -- Query 2: Calculate CTR and CVR
        SELECT 
            campaign_id,
            platform,
            SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) as impressions,
            SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
            SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions,
            SUM(revenue) as total_revenue,
            CASE 
                WHEN SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) > 0 
                THEN CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE) / 
                     CAST(SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) AS DOUBLE)
                ELSE 0.0 
            END as ctr,
            CASE 
                WHEN SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) > 0 
                THEN CAST(SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) AS DOUBLE) / 
                     CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE)
                ELSE 0.0 
            END as cvr
        FROM campaign_events
        GROUP BY campaign_id, platform
        ORDER BY campaign_id, platform;
        
