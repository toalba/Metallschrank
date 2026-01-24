-- PostgreSQL initialization script
-- This runs automatically on first container start

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic schema if needed (Alembic will handle actual tables)
-- This is just for any additional setup

-- Ensure proper encoding
ALTER DATABASE inventory SET timezone TO 'UTC';
