-- Initialize the database
CREATE DATABASE IF NOT EXISTS countrycompare;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE countrycompare TO postgres;
