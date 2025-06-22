-- ====================================
-- SUPABASE DATABASE SCHEMA FOR GITA
-- ====================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table - stores video metadata
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path VARCHAR(500) NOT NULL, -- Supabase storage path
    file_size_mb DECIMAL(10,2),
    duration_seconds DECIMAL(10,2),
    fps DECIMAL(8,2),
    resolution VARCHAR(20), -- e.g., "1920x1080"
    frame_count INTEGER,
    
    -- Trim information
    trim_start DECIMAL(10,2),
    trim_end DECIMAL(10,2),
    trim_duration DECIMAL(10,2),
    
    -- Vision analysis
    vision_analysis TEXT, -- Stores the generated music prompt from vision analysis
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, analyzed, completed, failed
    frames_extracted BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Frames table - stores individual frame metadata
CREATE TABLE frames (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Supabase storage path
    file_size_kb DECIMAL(10,2),
    
    -- Frame details
    frame_number INTEGER NOT NULL,
    timestamp_seconds DECIMAL(10,2) NOT NULL,
    
    -- Analysis results (for future AI analysis)
    vision_analysis JSONB, -- Store AI analysis results
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Music generation table - stores generated music info
CREATE TABLE music_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    
    -- Input prompts
    vision_prompt TEXT,
    music_prompt TEXT,
    
    -- Generated music
    music_file_path VARCHAR(500), -- Supabase storage path
    music_file_size_mb DECIMAL(10,2),
    
    -- Final output
    final_video_path VARCHAR(500), -- Supabase storage path
    
    -- Status
    generation_status VARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Final videos table - stores combined video+audio results
CREATE TABLE final_videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Supabase storage path
    file_size_mb DECIMAL(10,2),
    duration_seconds DECIMAL(10,2),
    
    -- Audio information
    audio_filename VARCHAR(255),
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX idx_videos_created_at ON videos(created_at);
CREATE INDEX idx_videos_status ON videos(processing_status);
CREATE INDEX idx_frames_video_id ON frames(video_id);
CREATE INDEX idx_frames_timestamp ON frames(timestamp_seconds);
CREATE INDEX idx_music_video_id ON music_generations(video_id);
CREATE INDEX idx_final_videos_original_id ON final_videos(original_video_id);
CREATE INDEX idx_final_videos_created_at ON final_videos(created_at);

-- RLS (Row Level Security) policies
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE frames ENABLE ROW LEVEL SECURITY;
ALTER TABLE music_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE final_videos ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (you can customize based on your auth needs)
CREATE POLICY "Enable read access for all users" ON videos FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON videos FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON videos FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON frames FOR SELECT USING (true);  
CREATE POLICY "Enable insert access for all users" ON frames FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON music_generations FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON music_generations FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON music_generations FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON final_videos FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON final_videos FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON final_videos FOR UPDATE USING (true);

-- Storage buckets setup (run these in Supabase Dashboard or via API)
-- These are the storage buckets you need to create in Supabase
/*
Buckets to create in Supabase Storage:
1. 'videos' - for uploaded video files
2. 'frames' - for extracted frame images  
3. 'music' - for generated music files
4. 'final-videos' - for final videos with music
*/ 