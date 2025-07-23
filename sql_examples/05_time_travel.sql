
        -- Show table history
        DESCRIBE HISTORY campaign_events;
        

        -- Query specific snapshot (replace 1 with actual snapshot ID)
        SELECT * FROM campaign_events FOR VERSION AS OF 1;
        

        -- Query specific timestamp
        SELECT * FROM campaign_events FOR TIMESTAMP AS OF '2024-01-01 10:00:00';
        
