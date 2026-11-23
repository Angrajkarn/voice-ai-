-- Database initialization script for VoiceAI
-- This runs when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas (optional, for organization)
-- CREATE SCHEMA IF NOT EXISTS voiceai;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (these will be created by Prisma migrations)
-- But we can add some custom ones here if needed

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE voiceai TO postgres;