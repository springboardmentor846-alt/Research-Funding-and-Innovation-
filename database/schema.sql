CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS researcher_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    organization VARCHAR(200),
    designation VARCHAR(100),
    research_domain VARCHAR(100),
    keywords TEXT,
    biography TEXT
);

CREATE TABLE IF NOT EXISTS grants (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    funding_amount FLOAT NOT NULL,
    deadline DATE NOT NULL,
    organization VARCHAR(255) NOT NULL,
    eligibility TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS funding_opportunities_v2 (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    agency VARCHAR(255) NOT NULL,
    funding_amount FLOAT NOT NULL,
    deadline DATE NOT NULL,
    country VARCHAR(100) NOT NULL,
    research_domain VARCHAR(100) NOT NULL,
    eligibility TEXT NOT NULL,
    description TEXT NOT NULL,
    application_link VARCHAR(500),
    status VARCHAR(50) DEFAULT 'Open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS publications_v2 (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    authors VARCHAR(500) NOT NULL,
    citation_count INTEGER DEFAULT 0,
    research_domain VARCHAR(100) NOT NULL,
    keywords TEXT NOT NULL,
    organization VARCHAR(255) NOT NULL
);