-- Initialize the database
-- Note: Database is already created by POSTGRES_DB environment variable

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    capital VARCHAR(100) NOT NULL,
    population BIGINT NOT NULL,
    area FLOAT NOT NULL,
    region VARCHAR(100) NOT NULL,
    subregion VARCHAR(100) NOT NULL,
    currency VARCHAR(50) NOT NULL,
    flag_url VARCHAR(255) NOT NULL,
    gdp FLOAT,
    gdp_per_capita FLOAT,
    hdi FLOAT,
    life_expectancy FLOAT,
    internet_penetration FLOAT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the comparisons table
CREATE TABLE IF NOT EXISTS comparisons (
    id SERIAL PRIMARY KEY,
    country1_name VARCHAR(100) NOT NULL,
    country2_name VARCHAR(100) NOT NULL,
    comparison_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(name);
CREATE INDEX IF NOT EXISTS idx_countries_region ON countries(region);
