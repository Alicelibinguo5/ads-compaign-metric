
        -- Add new columns to campaign_events table
        ALTER TABLE campaign_events ADD COLUMN attribution_source STRING;
        ALTER TABLE campaign_events ADD COLUMN user_segment STRING;
        ALTER TABLE campaign_events ADD COLUMN experiment_variant STRING;
        

        -- Update existing data with new column values
        UPDATE campaign_events 
        SET attribution_source = 'organic', user_segment = 'high_value', experiment_variant = 'control'
        WHERE user_id = 'user_001';
        
