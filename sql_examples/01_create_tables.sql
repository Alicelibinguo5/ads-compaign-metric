
        -- Create campaign events table
        CREATE TABLE IF NOT EXISTS campaign_events (
            event_id STRING,
            user_id STRING,
            campaign_id STRING,
            event_type STRING,
            platform STRING,
            timestamp TIMESTAMP(3),
            revenue DOUBLE,
            currency STRING,
            country STRING,
            device_type STRING,
            app_version STRING,
            creative_id STRING,
            placement_id STRING,
            metadata STRING,
            processed_at TIMESTAMP(3)
        ) PARTITIONED BY (campaign_id, platform, event_type)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        );
        

        -- Create user profiles table
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id STRING,
            age INT,
            gender STRING,
            country STRING,
            language STRING,
            platform STRING,
            registration_date TIMESTAMP(3),
            last_active TIMESTAMP(3),
            total_revenue DOUBLE,
            total_events INT,
            preferences STRING,
            updated_at TIMESTAMP(3),
            PRIMARY KEY (user_id) NOT ENFORCED
        ) PARTITIONED BY (country, platform)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        );
        

        -- Create campaign summaries table
        CREATE TABLE IF NOT EXISTS campaign_summaries (
            campaign_id STRING,
            date STRING,
            platform STRING,
            impressions BIGINT,
            clicks BIGINT,
            conversions BIGINT,
            revenue DOUBLE,
            ctr DOUBLE,
            cvr DOUBLE,
            cpc DOUBLE,
            cpa DOUBLE,
            roas DOUBLE,
            unique_users BIGINT,
            new_users BIGINT,
            created_at TIMESTAMP(3),
            updated_at TIMESTAMP(3),
            PRIMARY KEY (campaign_id, date, platform) NOT ENFORCED
        ) PARTITIONED BY (date, platform)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        );
        
